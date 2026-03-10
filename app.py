import os
import sys
import types
import pickle
import re
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from flask import Flask, request, render_template
from flask_cors import CORS
from bson.objectid import ObjectId
from flask.json.provider import DefaultJSONProvider

# Configurations
from config import SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD
from extensions import mail, login_manager
from models.user_model import User

# Controllers (Blueprints)
from controllers.auth_controller import auth_bp
from controllers.book_controller import book_bp
from controllers.wishlist_controller import wishlist_bp
from controllers.public_controller import public_bp
from controllers.user_controller import user_bp
from controllers.admin_controller import admin_bp

from flask import url_for as original_url_for
from werkzeug.routing import BuildError

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

# JSON Encoder for MongoDB ObjectId
class MongoJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json = MongoJSONProvider(app)

# Email Settings
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

# Init Extensions
mail.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Setup Upload Folders
UPLOAD_FOLDERS = [
    'static/uploads/profiles',
    'static/uploads/authors',
    'static/uploads/books/covers',
    'static/uploads/books/pdfs'
]

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDERS[0]
app.config['UPLOAD_FOLDER_AUTHOR'] = UPLOAD_FOLDERS[1]
app.config['UPLOAD_FOLDER_BOOKS_COVERS'] = UPLOAD_FOLDERS[2]
app.config['UPLOAD_FOLDER_BOOKS_PDFS'] = UPLOAD_FOLDERS[3]

for folder in UPLOAD_FOLDERS:
    os.makedirs(folder, exist_ok=True)


# ==========================================
# NLP BOOK SEARCH SETUP STARTS HERE
# ==========================================

PKL_PATH = "artifacts/neural_book_search_full.pkl"   # PKL with meta inside

# 1. Fix pickle loading (numpy._core issue)
def _install_numpy_core_shim():
    try:
        import numpy.core as ncore
        if "numpy._core" not in sys.modules:
            shim = types.ModuleType("numpy._core")
            shim.__dict__.update(ncore.__dict__)
            sys.modules["numpy._core"] = shim
    except Exception:
        pass

# 2. Encoder architecture (must match training)
def make_encoder(features: int) -> tf.keras.Model:
    inp = tf.keras.Input(shape=(features,), name="tfidf_input")
    x = tf.keras.layers.Dense(512, activation="relu")(inp)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(128)(x)
    out = tf.keras.layers.Lambda(lambda t: tf.math.l2_normalize(t, axis=1), name="l2norm")(x)
    return tf.keras.Model(inp, out)

# 3. Load PKL bundle
def load_bundle(pkl_path: str):
    if not os.path.exists(pkl_path):
        raise FileNotFoundError(f"PKL not found: {pkl_path}")

    _install_numpy_core_shim()

    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    required = ["book_ids", "doc_embeddings", "tfidf_model",
                "query_encoder_weights", "doc_encoder_weights", "max_features", "meta"]
    for k in required:
        if k not in data:
            raise KeyError(f"Missing '{k}' in PKL. Re-save PKL with meta.")

    book_ids = [str(x).strip() for x in data["book_ids"]]
    doc_emb = np.array(data["doc_embeddings"], dtype=np.float32)
    vectorizer = data["tfidf_model"]
    features = int(data["max_features"])
    meta = data["meta"]

    for mk in ["title", "authors", "description", "thumbnail"]:
        if mk not in meta or not isinstance(meta[mk], list) or len(meta[mk]) != len(book_ids):
            meta[mk] = [""] * len(book_ids)

    if doc_emb.shape[0] != len(book_ids):
        raise ValueError("doc_embeddings rows != book_ids length. Re-save correctly.")

    query_encoder = make_encoder(features)
    doc_encoder = make_encoder(features)
    query_encoder.set_weights(data["query_encoder_weights"])
    doc_encoder.set_weights(data["doc_encoder_weights"])

    _ = query_encoder(np.zeros((1, features), dtype=np.float32), training=False).numpy()

    return book_ids, doc_emb, vectorizer, query_encoder, meta

# 4. Query cleaner
STOPWORDS = set(ENGLISH_STOP_WORDS)
def clean_query(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return " ".join(words)

# 5. Hybrid Search (TF-IDF shortlist + Neural rerank)
def hybrid_search(query: str, k=10, pre_k=200):
    query = clean_query(query)
    if not query:
        return []

    k = max(1, min(int(k), len(BOOK_IDS)))
    pre_k = max(k, min(int(pre_k), len(BOOK_IDS)))

    # Step 1: TF-IDF shortlist
    q_vec = normalize(VECTORIZER.transform([query]))
    sims_tfidf = cosine_similarity(q_vec, X_ALL_TFIDF).ravel()

    idx = np.argpartition(-sims_tfidf, pre_k - 1)[:pre_k]
    idx = idx[np.argsort(-sims_tfidf[idx])]

    # Step 2: Neural rerank
    q_dense = q_vec.toarray().astype(np.float32)
    q_emb = Q_ENCODER(q_dense, training=False).numpy().astype(np.float32)  # (1,128)

    doc_subset = DOC_EMB[idx]  # (pre_k, 128)
    sims_nn = (q_emb @ doc_subset.T).ravel()

    top = np.argsort(-sims_nn)[:k]
    final_idx = idx[top]

    results = []
    for rank_pos, doc_i in enumerate(final_idx):
        results.append({
            "isbn13": BOOK_IDS[doc_i],
            "score": float(sims_nn[top[rank_pos]]),
            "title": (META["title"][doc_i] or "").strip(),
            "authors": (META["authors"][doc_i] or "").strip(),
            "description": (META["description"][doc_i] or "").strip(),
            "thumbnail": (META["thumbnail"][doc_i] or "").strip(),
        })

    return results

# 6. Startup load
STARTUP_ERROR = ""
try:
    BOOK_IDS, DOC_EMB, VECTORIZER, Q_ENCODER, META = load_bundle(PKL_PATH)

    # TF-IDF matrix for ALL books (used for shortlist)
    all_text = []
    for i in range(len(BOOK_IDS)):
        t = META["title"][i] if META["title"][i] else ""
        a = META["authors"][i] if META["authors"][i] else ""
        d = META["description"][i] if META["description"][i] else ""
        all_text.append(f"{t} {a} {d}".strip())

    X_ALL_TFIDF = normalize(VECTORIZER.transform(all_text))

except Exception as e:
    STARTUP_ERROR = str(e)
    BOOK_IDS, DOC_EMB, VECTORIZER, Q_ENCODER, META = [], None, None, None, {}
    X_ALL_TFIDF = None

# ==========================================
# NLP BOOK SEARCH SETUP ENDS HERE
# ==========================================


# Register Blueprints
app.register_blueprint(public_bp)              # (/, /category, /author)
app.register_blueprint(user_bp)                #(/view_profile, history)
app.register_blueprint(admin_bp, url_prefix='/admin_actions')  # Admin
app.register_blueprint(auth_bp, url_prefix='/auth')            # Login/Register, Admin Dashboard Render
app.register_blueprint(book_bp, url_prefix='/api/books')       # Book Search APIs
app.register_blueprint(wishlist_bp, url_prefix='/')            # Wishlist APIs


@app.context_processor
def override_url_for():
    def custom_url_for(endpoint, **values):
        try:
            # මුලින්ම සාමාන්‍ය විදියට වැඩ කරනවාදැයි බලයි (static ෆයිල් වලට මෙය අවශ්‍යයි)
            return original_url_for(endpoint, **values)
        except BuildError:
            # Error එකක් ආවොත්, පරණ නම අලුත් Blueprint නමට මාරු කරයි
            endpoint_map = {
                'home': 'public_bp.home',
                'category': 'public_bp.category',
                'view_category_books': 'public_bp.view_category_books',
                'author': 'public_bp.author',
                'author_profile': 'public_bp.author_profile',
                'show_book_page': 'public_bp.show_book_page',
                'read_book': 'public_bp.read_book',
                'contact': 'public_bp.contact',
                
                'view_profile': 'user_bp.view_profile',
                'update_profile': 'user_bp.update_profile',
                
                'login': 'auth_bp.login',
                'register': 'auth_bp.register',
                'logout': 'auth_bp.logout',
                'forgot_password': 'auth_bp.forgot_password',
                'reset_password_page': 'auth_bp.reset_password_page',
                'admin_dashboard': 'auth_bp.admin_dashboard',
            }
            
            # මැප් එකේ නම තියෙනවා නම් අලුත් එකට හරවා යවයි
            if endpoint in endpoint_map:
                return original_url_for(endpoint_map[endpoint], **values)
            
            # නැත්නම් Error එක පෙන්නයි
            raise

    return dict(url_for=custom_url_for)


# --- NLP Search Route ---
@app.route("/nlp_search", methods=["GET", "POST"])
def nlp_search_index():
    query = ""
    top_k = 10
    results = []
    error = STARTUP_ERROR

    if request.method == "POST":
        query = (request.form.get("q") or "").strip()
        try:
            top_k = int(request.form.get("k") or 10)
        except:
            top_k = 10

        if not error:
            try:
                results = hybrid_search(query, k=top_k, pre_k=200)
            except Exception as e:
                error = str(e)

    return render_template(
        "deep_search.html",
        query=query,
        top_k=top_k,
        results=results,
        error=error,
        n_books=len(BOOK_IDS)
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
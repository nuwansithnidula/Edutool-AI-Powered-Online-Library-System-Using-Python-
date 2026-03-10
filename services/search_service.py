import os
import sys
import torch
from sentence_transformers import SentenceTransformer, util
# Add the parent directory to sys.path so 'models' can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.book_model import BookModel

EMBEDDING_PATH = "artifacts/embeddings.pt"

class SBERTSearchService:
    _instance = None

    def __new__(cls):
        """Singleton Pattern Implementation"""
        if cls._instance is None:
            cls._instance = super(SBERTSearchService, cls).__new__(cls)
            print("Initializing AI Service...")
            
            cls._instance.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            cls._instance.book_model = BookModel()
            cls._instance.load_data_and_embeddings()
            
        return cls._instance

    def load_data_and_embeddings(self):
        print("🔄 Fetching books from MongoDB...")
        self.books = self.book_model.get_all_books() 
        
        if os.path.exists(EMBEDDING_PATH) and len(self.books) > 0:
            print("📂 Loading embeddings from Disk (artifacts/embeddings.pt)...")
            loaded_embeddings = torch.load(EMBEDDING_PATH)

            if len(self.books) == loaded_embeddings.shape[0]:
                self.embeddings = loaded_embeddings
                print("✅ Embeddings Loaded Successfully from Disk!")
                return
            else:
                print("⚠️ Data Mismatch! (DB vs File). Re-indexing everything...")
        
        self.reindex_all()

    def _get_combined_text(self, book):
        title = str(book.get('title', ''))
        published_year = str(book.get('published_year', ''))
        description = str(book.get('description', ''))
        
        author_ids = book.get('author_ids', [])
        category_ids = book.get('category_ids', [])
        
        author_names = self.book_model.get_author_names_by_ids(author_ids)
        category_names = self.book_model.get_category_names_by_ids(category_ids)
        
        authors_str = " ".join(author_names)
        categories_str = " ".join(category_names)
        
        combined_text = f"{title} {published_year} {description} {authors_str} {categories_str}"
        return combined_text.strip()

    # --- 🔥 අලුතින් එකතු කළ කොටස: Frontend එකට ගැලපෙන ලෙස දත්ත හැඩගැස්වීම ---
    # --- search_service.py හි ඇති _format_book_for_frontend කොටස ---
    
    def _format_book_for_frontend(self, book_dict, score=None):
        """Preparing data into the format expected by the frontend"""
        book = book_dict.copy()
        
        # 1. Converting ID to String
        if '_id' in book:
            book['id'] = str(book['_id'])
            book.pop('_id', None)
            
        # 2. Adding the Match Score
        if score is not None:
            book['match_score'] = round(score * 100, 2)
            
        # 3. Converting the Authors Array to a Single String
        author_ids = book.get('author_ids', [])
        author_names = self.book_model.get_author_names_by_ids(author_ids)
        book['authors'] = ", ".join(author_names) if author_names else "Unknown"
        
        # Getting category names
        category_ids = book.get('category_ids', [])
        category_names = self.book_model.get_category_names_by_ids(category_ids)
        book['categories'] = category_names
 
        # 4. Cover Image Path
        cover = book.get('cover_image', '')
        if cover:
            book['thumbnail'] = f"/static/uploads/books/covers/{cover}"
        else:
            book['thumbnail'] = "https://placehold.co/400x600/1e1e2e/ffffff?text=No+Cover"
            
        return book


    def reindex_all(self):
        if not self.books:
            self.embeddings = None
            return

        print(" Generating new embeddings (This might take a moment)...")
        combined_texts = [self._get_combined_text(book) for book in self.books]
        self.embeddings = self.model.encode(combined_texts, convert_to_tensor=True)
        
        os.makedirs(os.path.dirname(EMBEDDING_PATH), exist_ok=True) 
        torch.save(self.embeddings, EMBEDDING_PATH)
        print(f" Saved embeddings to {EMBEDDING_PATH}")


    def search(self, query):
        if self.embeddings is None or not self.books:
            return []

        query_vec = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_vec, self.embeddings)[0]
        
        print(f"\n Searching for: {query}")
        
        all_results = []
        for i in range(len(self.books)):
            score = float(cos_scores[i])

            formatted_book = self._format_book_for_frontend(self.books[i], score)
            all_results.append(formatted_book)
            
        all_results.sort(key=lambda x: x['match_score'], reverse=True)
        final_results = [book for book in all_results[:8] if book['match_score'] > 15]

        return final_results

    def add_book_and_index(self, book_data):
        self.book_model.add_book(book_data)
        new_text = self._get_combined_text(book_data)
        new_embedding = self.model.encode(new_text, convert_to_tensor=True)
        
        self.books.append(book_data) 
        
        if self.embeddings is None:
            self.embeddings = new_embedding.unsqueeze(0)
        else:
            self.embeddings = torch.cat((self.embeddings, new_embedding.unsqueeze(0)), 0)
            
        torch.save(self.embeddings, EMBEDDING_PATH)
        print("Updated embeddings.pt file with new book!")

    def get_recommendations(self, book_title):
        if self.embeddings is None or not self.books:
            return []

        target_idx = -1
        search_title_str = str(book_title).strip().lower()

        for idx, book in enumerate(self.books):
            current_book_title = str(book.get('title', '')).strip().lower()
            if current_book_title == search_title_str:
                target_idx = idx
                break
        
        if target_idx == -1:
            return [] 

        target_embedding = self.embeddings[target_idx]
        cos_scores = util.cos_sim(target_embedding, self.embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(6, len(self.books))) 

        recommendations = []
        for score, idx in zip(top_results.values, top_results.indices):
            idx_int = idx.item()       
            score_float = score.item()
            
            if idx_int != target_idx and score_float > 0.2:
                # 🔥 Format කරපු දත්ත පමණක් යවන්න
                formatted_book = self._format_book_for_frontend(self.books[idx_int], score_float)
                recommendations.append(formatted_book)

        return recommendations

    def picked_for_you(self, queries):
        if not queries:
            return []

        combined_query = " ".join(queries)
        results = self.search(combined_query) 
        return results[:8]
    
    def get_book_by_id(self, book_id):
        if not self.books:
            return None

        # 1. Index Search
        try:
            idx = int(book_id)
            if 0 <= idx < len(self.books):
                return self._format_book_for_frontend(self.books[idx])
        except ValueError:
            pass 

        # 2. ObjectId Search
        search_id = str(book_id).strip()
        for book in self.books:
            if str(book.get('_id', '')) == search_id:
                return self._format_book_for_frontend(book)

        return None

if __name__ == "__main__":
    print("🚀 Starting Search Service Test...")
    search_engine = SBERTSearchService()
    test_query = "technology and future"
    
    print(f"\n🧪 Testing Search for: '{test_query}'")
    results = search_engine.search(test_query)
    
    if results:
        for idx, book in enumerate(results):
            print(f"[{idx+1}] Title: {book.get('title', 'Unknown')} | Score: {book.get('match_score', 0)}%")
    else:
        print("❌ No results found.")
        
    print("\n✅ Test Complete!")
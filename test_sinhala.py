from sentence_transformers import SentenceTransformer, util

# Multilingual මොඩලය
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 1. ඉංග්‍රීසි පොත් විස්තරය (Database එකේ ඇති ආකාරයට)
english_text = ["This book explains how computers work and basic coding."]

# 2. සිංහල සෙවුම් පදය (Search Query)
sinhala_query = "පරිගණක සහ ක්‍රමලේඛනය ගැන පොත්"

# Vectors බවට පත් කිරීම
emb1 = model.encode(english_text)
emb2 = model.encode(sinhala_query)

# සමානකම බැලීම
score = util.cos_sim(emb1, emb2)

print(f"Similarity Score: {score.item()}")

if score.item() > 0.4:
    print("✅ සාර්ථකයි! සිංහල සහ ඉංග්‍රීසි ගැලපේ.")
else:
    print("❌ අසාර්ථකයි! ගැලපීම මදි.")
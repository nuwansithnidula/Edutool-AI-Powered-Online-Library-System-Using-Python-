import pandas as pd
from services.search_service import SBERTSearchService

def run_advanced_evaluation():
    print("Starting Advanced NLP Model Evaluation...\n")
    search_engine = SBERTSearchService()
    
    test_queries = [
        {"query": "cat bringing joy to dreary town", "expected_title": "The Cat That Made Nothing Something Again"},
        {"query": "cat making nothing into something", "expected_title": "The Cat That Made Nothing Something Again"},
        {"query": "Captain Thompson in space", "expected_title": "Thompson's Cat"},
        {"query": "space cruiser landing cat", "expected_title": "Thompson's Cat"},
        {"query": "dystopian post-Rupture world", "expected_title": "The Demon Girl"},
        {"query": "demon girl humanity", "expected_title": "The Demon Girl"},
        {"query": "military captain hilary roding", "expected_title": "Mademoiselle At Arms"},
        {"query": "abby brown divorcee taking chances", "expected_title": "Taking Chances (The Davis Twins Series - Book 1)"},
        {"query": "davis twins book 1", "expected_title": "Taking Chances (The Davis Twins Series - Book 1)"},
        {"query": "detective demon summoner paige", "expected_title": "Whiskey Witches"}
    ]

    top_1_hits = 0
    top_8_hits = 0
    mrr_score = 0.0

    print(f"{'Search Query':<45} | {'Rank Found'} | {'Score'}")
    print("-" * 75)

    for case in test_queries:
        query = case['query']
        expected_title = case['expected_title'].lower().strip()
        
        # Search through the search service
        results = search_engine.search(query)
        
        rank = 0
        found = False
        
        # Check if the results contain the correct book
        for i, res in enumerate(results):
            current_title = res.get('title', '').lower().strip()
            if current_title == expected_title:
                rank = i + 1
                found = True
                break
        
        # Calculating Metrics
        if found:
            if rank == 1:
                top_1_hits += 1
            if rank <= 8:
                top_8_hits += 1
                
            current_mrr = 1.0 / rank
            mrr_score += current_mrr
            print(f"{query:<45} | {rank:>10} | {current_mrr:.2f}")
        else:
            print(f"{query:<45} | {'Not Found':>10} | 0.00")

    # Final percentage calculation
    total_queries = len(test_queries)
    if total_queries == 0:
        return

    top_1_accuracy = (top_1_hits / total_queries) * 100
    top_8_accuracy = (top_8_hits / total_queries) * 100
    final_mrr = (mrr_score / total_queries) * 100

    print("-" * 75)
    print("\n --- FINAL ADVANCED ACCURACY REPORT ---")
    print(f"Top-1 Accuracy (The probability that the first result is correct): {top_1_accuracy:.2f}%")
    print(f"Top-8 Accuracy (Probability of being in the top 8):    {top_8_accuracy:.2f}%")
    print(f"MRR / Overall NLP Score (Overall quality):        {final_mrr:.2f}%")
    print("------------------------------------------")

if __name__ == "__main__":
    run_advanced_evaluation()
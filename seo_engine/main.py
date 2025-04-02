import os
import json
from query_generator import generate_queries
from competitor_analysis import analyze_competitors
from seo_scraper import SEOScraper
from metadata_extractor import extract_metadata
from keyword_extractor import KeywordExtractor
from openpagerank_analysis import analyze_pagerank
from seo_analyser import SEOAnalyzer
from search_intent import SearchIntentClassifier
from filter_backlinks import filter_backlinks
from rag_generator import RAGGenerator
from rag_retriever import RAGRetriever
from seo_report_generator import generate_report
from build_index import build_faiss_index
import time

def save_comprehensive_json(file_path, **kwargs):
    """Saves all provided data into a single structured JSON file."""
    print(f"\n💾 Saving comprehensive analysis results to {file_path}...")
    # Create a structured dictionary
    comprehensive_data = {
        "input_domain": kwargs.get("domain", "N/A"),
        "input_niche": kwargs.get("niche", "N/A"),
        "generated_queries": kwargs.get("queries", []),
        "competitors": kwargs.get("competitor_domains", []),
        "metadata_summary": [
            {"url": item.get("url", "N/A"), "title": item.get("title", "N/A")} 
            for item in kwargs.get("all_metadata", [])
        ], # Summarized metadata
        "keywords": kwargs.get("keyword_data", {}),
        "pagerank": kwargs.get("pagerank_data", {}),
        "backlinks": kwargs.get("backlink_data", {}),
        "search_intents": kwargs.get("intent_data", {}),
        "analysis_scores": kwargs.get("seo_analysis", {}),
        "ai_content": kwargs.get("refined_content", "N/A")
    }
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Comprehensive JSON saved successfully.")
    except Exception as e:
        print(f"❌ Error saving comprehensive JSON: {e}")

def main():
    """Main workflow execution"""
    print("\n🚀 Starting SEO Analysis Pipeline")
    
    # ✅ Get Domain & Niche from User
    domain = input("\n🌐 Enter the domain for SEO analysis (e.g., example.com): ").strip()
    niche = input("\n🏷️ Enter the niche for this domain (e.g., E-commerce, Healthcare, Technology): ").strip()
    
    # ✅ Step 1: Generate SEO Queries
    print("\n🔍 Step 1: Generating SEO queries...")
    queries = generate_queries(domain)
    
    # ✅ Step 2: Competitor Analysis
    print("\n🔍 Step 2: Analyzing competitors...")
    competitor_domains = analyze_competitors(queries)
    
    # ✅ Step 3: SEO Scraping
    print("\n🔍 Step 3: Scraping competitor data...")
    scraper = SEOScraper()
    scraped_data = scraper.scrape_competitors()
    
    # ✅ Step 4: Metadata Extraction
    print("\n🔍 Step 4: Extracting metadata...")
    all_metadata = []
    if scraped_data:
        for item in scraped_data:
            url = item.get('url')
            if url:
                print(f"Extracting metadata for {url}...")
                metadata = extract_metadata(url)
                metadata['url'] = url # Add URL for reference
                all_metadata.append(metadata)
                time.sleep(0.5) # Small delay
            else:
                print("⚠️ Skipping item with no URL in scraped data")
    else:
        print("⚠️ No scraped data available for metadata extraction")
    
    # ✅ Step 5: Keyword Extraction
    print("\n🔍 Step 5: Extracting keywords...")
    keyword_extractor = KeywordExtractor()
    keyword_data = keyword_extractor.process_competitor_data()
    
    # ✅ Step 6: PageRank Analysis
    print("\n🔍 Step 6: Analyzing PageRank...")
    pagerank_data = analyze_pagerank(competitor_domains)
    
    # ✅ Step 7: Backlink Analysis
    print("\n🔍 Step 7: Analyzing backlinks...")
    backlink_data = filter_backlinks(competitor_domains, niche)
    
    # ✅ Step 8: Search Intent Analysis
    print("\n🔍 Step 8: Analyzing search intent...")
    intent_classifier = SearchIntentClassifier()
    intent_data = intent_classifier.analyze_search_intents()
    
    # ✅ Step 9: SEO Analysis
    print("\n🔍 Step 9: Performing comprehensive SEO analysis...")
    seo_analyzer = SEOAnalyzer()
    seo_analysis = seo_analyzer.generate_seo_analysis()
    
    # ✅ Step 9.5: Build/Rebuild FAISS Index (Crucial before RAG)
    print("\n🔨 Step 9.5: Building FAISS index...")
    index_built = build_faiss_index()
    if not index_built:
        print("❌ FAISS index building failed. Cannot proceed with RAG steps.")
        print("\n🔴 SEO Analysis Pipeline Halted due to index build failure.")
        return
    
    # ✅ Step 10: RAG Content Generation
    print("\n🔍 Step 10: Generating AI-enhanced content...")
    rag_generator = RAGGenerator()
    rag_content = rag_generator.generate_content(seo_analysis, keyword_data)
    
    # ✅ Step 11: RAG Content Refinement
    print("\n🔍 Step 11: Refining AI content...")
    rag_retriever = RAGRetriever()
    refined_content = rag_retriever.refine_content(rag_content, seo_analysis)
    
    # ✅ Step 11.5: Save Comprehensive JSON Data
    save_comprehensive_json(
        "output/comprehensive_seo_results.json",
        domain=domain,
        niche=niche,
        queries=queries,
        competitor_domains=competitor_domains,
        all_metadata=all_metadata,
        keyword_data=keyword_data,
        pagerank_data=pagerank_data,
        backlink_data=backlink_data,
        intent_data=intent_data,
        seo_analysis=seo_analysis,
        refined_content=refined_content
    )
    
    # ✅ Step 12: Generate Final Report (PDF)
    print("\n📊 Step 12: Generating comprehensive SEO report (PDF)...")
    # Check if seo_analysis is valid before proceeding
    if not seo_analysis or not isinstance(seo_analysis, dict):
        print("❌ Cannot generate PDF report: SEO analysis data is missing or invalid.")
    else:
        generate_report(
            seo_analysis=seo_analysis,
            keyword_data=keyword_data,
            competitor_data=competitor_domains,
            backlink_data=backlink_data,
            intent_data=intent_data,
            rag_content=refined_content
        )
    
    print("\n✅ SEO Analysis Pipeline Completed Successfully!")
    # Update final message to mention both files
    print(f"📄 JSON results saved to: output/comprehensive_seo_results.json")
    if seo_analysis and isinstance(seo_analysis, dict): # Only mention PDF if generation was attempted
        print(f"📄 PDF report saved to: output/seo_report.pdf")

if __name__ == "__main__":
    main()

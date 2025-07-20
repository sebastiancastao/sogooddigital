"""
Example usage of the Task Assigner
"""

from task_assigner import TaskAssigner
import json

def main():
    """Example of using the Task Assigner programmatically"""
    
    # Example Google Doc ID (replace with your actual document ID)
    # You can get this from the Google Doc URL:
    # https://docs.google.com/document/d/DOC_ID/edit
    doc_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    try:
        # Initialize the task assigner
        print("Initializing Task Assigner...")
        assigner = TaskAssigner()
        
        # Process the Google Doc
        print(f"Processing Google Doc: {doc_id}")
        results = assigner.process_google_doc(doc_id)
        
        # Display results
        print("\n" + "="*60)
        print("TASK ASSIGNMENT RESULTS")
        print("="*60)
        
        print(f"📄 Total tasks extracted: {results['total_tasks']}")
        print(f"✅ Trello cards created: {len(results['trello_cards'])}")
        
        # Show assignment breakdown
        print("\n👥 Task assignments:")
        for assignee, count in results['assignments'].items():
            print(f"  • {assignee}: {count} tasks")
        
        # Show created Trello cards
        print("\n📋 Trello cards created:")
        for card in results['trello_cards']:
            print(f"  • {card['task']}")
            print(f"    → Assigned to: {card['assignee']}")
            print(f"    → Card URL: {card['card_url']}")
            print()
        
        # Show any errors
        if results['errors']:
            print(f"\n❌ Errors encountered ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  • {error}")
        
        # Save detailed results to JSON file
        with open('task_assignment_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\n💾 Detailed results saved to 'task_assignment_results.json'")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
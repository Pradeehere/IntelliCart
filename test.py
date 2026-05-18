import recommender
import json

try:
    recs = recommender.get_user_based_recommendations("U001")
    print(json.dumps(recs, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    recs = recommender.get_item_based_recommendations("U001")
    print(json.dumps(recs, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()

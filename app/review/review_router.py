# app/review/review_router.py
"""
FastAPI router for MongoDB-based review preprocessing using site-specific processors.
"""
from fastapi import APIRouter, HTTPException, status
from database.mongodb_connection import mongo_db
from review_analysis.preprocessing.catchtable_processor import CatchtableProcessor
from review_analysis.preprocessing.googlemap_processor import GooglemapProcessor
from review_analysis.preprocessing.kakaomap_processor import KakaoMapProcessor
from pymongo.collection import Collection

router = APIRouter(prefix="/review", tags=["review"])

# Factory to select the appropriate processor
def get_processor(site_name: str):
    name = site_name.lower()
    if name == "catchtable":
        return CatchtableProcessor
    if name == "googlemap":
        return GooglemapProcessor
    if name == "kakaomap":
        return KakaoMapProcessor
    return None

@router.post(
    "/preprocess/{site_name}",
    status_code=status.HTTP_200_OK,
    summary="Preprocess raw reviews for a given site"
)
def preprocess(site_name: str):
    """
    Fetch raw documents, process using the site-specific processor, and store results.
    """
    # 1) Raw collection
    raw_col: Collection = mongo_db.get_collection(site_name)
    total = raw_col.count_documents({})
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No documents found in collection '{site_name}'"
        )

    # 2) Load raw docs
    raw_docs = list(raw_col.find({}))

    # 3) Select processor class and instantiate
    proc_cls = get_processor(site_name)
    if proc_cls is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No processor for site '{site_name}'"
        )
    # Use temp CSV adapter
    import os, tempfile, pandas as pd
    with tempfile.TemporaryDirectory() as tmpdir:
        in_csv = os.path.join(tmpdir, f"{site_name}_raw.csv")
        out_dir = tmpdir
        # Write raw docs to CSV
        df = pd.DataFrame([{k: v for k, v in doc.items() if k != '_id'} for doc in raw_docs])
        df.to_csv(in_csv, index=False)

        # Process pipeline
        processor = proc_cls(in_csv, out_dir)
        processor.preprocess()
        processor.feature_engineering()
        processor.save_to_database()

        # Read processed CSV and push back to MongoDB
        out_csv = os.path.join(out_dir, f"preprocessed_reviews_{site_name}.csv")
        if not os.path.exists(out_csv):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Processing failed: no output generated"
            )
        df_out = pd.read_csv(out_csv)
        processed_col: Collection = mongo_db.get_collection(f"{site_name}_processed")
        processed_col.delete_many({})
        processed_col.insert_many(df_out.to_dict(orient="records"))

    return {
        "site_name": site_name,
        "input_count": total,
        "processed_count": len(df_out),
    }

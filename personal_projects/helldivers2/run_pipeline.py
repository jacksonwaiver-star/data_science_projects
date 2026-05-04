from personal_projects.helldivers2.data_pipeline.pipeline import run_incremental_pipeline

if __name__ == "__main__":
    df = run_incremental_pipeline()
    print("Pipeline finished. Rows:", len(df))
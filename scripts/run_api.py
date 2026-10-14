"""
Headless runner to launch the enterprise FastAPI REST microservice.
Usage:
    python scripts/run_api.py --port 8000 --host 0.0.0.0
"""
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Run the Autonomous Document Intelligence REST API")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print(f"🚀 Starting Autonomous Document Intelligence API on http://{args.host}:{args.port}")
    print(f"📚 OpenAPI Documentation available at http://{args.host}:{args.port}/docs")
    uvicorn.run("src.api.server:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()

"""
Script de inicialização do servidor API.

Uso:
    python run_api.py
    python run_api.py --port 8000 --reload
"""
import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Regeneration Credit AI Assistant API")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Porta (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload em dev")
    parser.add_argument("--workers", type=int, default=1, help="Workers (default: 1)")
    parser.add_argument("--log-level", default="info", help="Log level (default: info)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("  Regeneration Credit AI Assistant API")
    print(f"  http://{args.host}:{args.port}")
    print(f"  Docs: http://{args.host}:{args.port}/api/v1/docs")
    print(f"{'='*60}\n")

    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()

import os
import random
import argparse
import subprocess

import json

from flask import (
   Flask,
   request,
   Response
)

app = Flask(__name__)

@app.route("/drain-node", methods=["POST"])
def drain_node():
    if request.method == "POST":
        subprocess.call(f"bash /home/ubuntu/DE1-Spark/DE-2025/spark-deploy/manager/drain.sh", shell=True)
        # return Response(json.dumps({"nodes": node_names}), 200)
        return Response("Successfully drained the ndoe!", 200)
    else:
        return Response("Only POST available!", 400)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        required=False,
        default="0.0.0.0",
        type=str,
    )
    parser.add_argument(
        "--port",
        required=False,
        default=5200,
        type=int,
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    app.run(host = args.host,port=args.port,debug=args.debug)
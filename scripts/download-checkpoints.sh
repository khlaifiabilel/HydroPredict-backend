#!/bin/bash
# Download model checkpoints from S3
# Usage: ./scripts/download-checkpoints.sh

set -e

S3_BUCKET="hydropredict-model-artifacts-387677210037"
CHECKPOINTS_DIR="checkpoints"
AWS_REGION="eu-central-1"

echo "🔄 Downloading model checkpoints from S3..."

# Create checkpoints directory if not exists
mkdir -p $CHECKPOINTS_DIR

# Download from S3
aws s3 sync \
  s3://${S3_BUCKET}/checkpoints/ \
  ${CHECKPOINTS_DIR}/ \
  --region ${AWS_REGION}

echo "✅ Checkpoints downloaded successfully!"
echo ""
echo "Downloaded files:"
ls -lh ${CHECKPOINTS_DIR}/


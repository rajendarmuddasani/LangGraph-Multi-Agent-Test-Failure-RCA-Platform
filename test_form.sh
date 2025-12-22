#!/bin/bash
# Test RCA Platform Form Submission

echo "🧪 Testing RCA Platform API..."
echo ""

# Test data
LOT_ID="LOT-2024-TEST-001"
WAFER_ID="W99"
BIN=7
PRIORITY="high"
USER_ID="test@engineer.com"

echo "📝 Submitting RCA Request..."
echo "   Lot ID: $LOT_ID"
echo "   Wafer ID: $WAFER_ID"
echo "   Bin: $BIN"
echo "   Priority: $PRIORITY"
echo ""

# Submit RCA
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"lot_id\": \"$LOT_ID\",
    \"wafer_id\": \"$WAFER_ID\",
    \"bin\": $BIN,
    \"priority\": \"$PRIORITY\",
    \"user_id\": \"$USER_ID\"
  }")

echo "✅ Response:"
echo "$RESPONSE" | python3 -m json.tool

# Extract session ID
SESSION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', 'N/A'))")

if [ "$SESSION_ID" != "N/A" ]; then
    echo ""
    echo "🎯 Session Created: $SESSION_ID"
    echo ""
    echo "📊 You can now:"
    echo "   • View Status: http://localhost:3000/status/$SESSION_ID"
    echo "   • Or use the UI form at: http://localhost:3000/submit"
else
    echo ""
    echo "❌ Error: No session ID received"
fi

echo ""
echo "✨ Backend is ready! Try the form at http://localhost:3000/submit"

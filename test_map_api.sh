#!/bin/bash

echo "========================================="
echo "Testing Map API for Puttur MLA"
echo "========================================="
echo ""

# Step 1: Request OTP
echo "1. Requesting OTP for Puttur MLA..."
curl -s -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226666"}' | jq '.'

echo ""
echo ""

# Step 2: Verify OTP and get token
echo "2. Verifying OTP and getting token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226666", "otp": "123456"}')

echo "$TOKEN_RESPONSE" | jq '.'

# Extract token
TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

echo ""
echo "Token: $TOKEN"
echo ""
echo ""

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token!"
  exit 1
fi

# Step 3: Get user info
echo "3. Getting current user info..."
curl -s -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo ""
echo ""

# Step 4: Get complaints
echo "4. Getting complaints for Puttur MLA..."
COMPLAINTS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/complaints/?page=1&page_size=100" \
  -H "Authorization: Bearer $TOKEN")

echo "$COMPLAINTS_RESPONSE" | jq '.'

echo ""
echo ""

# Step 5: Count complaints with coordinates
echo "5. Analyzing complaints..."
TOTAL=$(echo "$COMPLAINTS_RESPONSE" | jq '.total')
WITH_COORDS=$(echo "$COMPLAINTS_RESPONSE" | jq '[.complaints[] | select(.lat != null and .lng != null)] | length')
WITHOUT_COORDS=$(echo "$COMPLAINTS_RESPONSE" | jq '[.complaints[] | select(.lat == null or .lng == null)] | length')

echo "Total complaints: $TOTAL"
echo "With coordinates: $WITH_COORDS"
echo "Without coordinates: $WITHOUT_COORDS"

echo ""
echo ""

# Step 6: Show sample complaints with coordinates
echo "6. Sample complaints with coordinates:"
echo "$COMPLAINTS_RESPONSE" | jq -r '.complaints[] | select(.lat != null and .lng != null) | "  - \(.title): lat=\(.lat), lng=\(.lng)"' | head -5

echo ""
echo ""

# Step 7: Show complaints without coordinates
echo "7. Sample complaints WITHOUT coordinates:"
echo "$COMPLAINTS_RESPONSE" | jq -r '.complaints[] | select(.lat == null or .lng == null) | "  - \(.title): lat=\(.lat), lng=\(.lng)"' | head -5

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="

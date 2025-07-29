# Address Extraction Issues and Fixes

## 🚨 Issues Identified

### 1. **Overly Strict Address Validation**
The original validation logic in `ai_extractor.py` was too restrictive:

```python
# OLD CODE - Too strict
if not re.search(r'\d', address) or not any(
    kw in address for kw in [
        "street", "road", "lane", "colony", "sector", "area", "block", "apartment", "flat"
    ]
):
    parsed_data["address"] = "N/A"
    parsed_data["pin_code"] = "N/A"
```

**Problem**: This rejected valid addresses like "Mumbai, Maharashtra" or "Bangalore 560001" because they didn't contain street-level keywords.

### 2. **Field Name Inconsistency**
- AI extracted to `"address"` field
- Enricher expected `"residential_address"` field
- This mismatch caused data loss during processing

### 3. **No Fallback Mechanism**
When AI failed to extract addresses, there was no backup pattern-matching approach.

### 4. **Limited City Recognition**
The AI prompt didn't handle Indian location patterns effectively.

---

## ✅ Solutions Implemented

### 1. **Improved Address Validation Logic**
Now accepts addresses based on multiple criteria:

```python
# NEW CODE - More flexible
has_digits = re.search(r'\d', address)
has_keywords = any(kw in address_lower for kw in [
    "street", "road", "lane", "colony", "sector", "area", "block", 
    "apartment", "flat", "nagar", "city", "town", "village", "dist",
    "district", "pincode", "pin", "zip"
])
has_indian_location = any(loc in address_lower for loc in indian_locations)
sufficient_length = len(address) >= 5

# Accept if ANY criteria is met
if has_digits or has_keywords or has_indian_location or sufficient_length:
    # Keep the address
```

### 2. **Enhanced AI Prompt**
Updated the prompt to be more liberal in address extraction:

```
**For address extraction: Extract ANY address information that appears to be the candidate's personal/residential address. This can include:**
- Complete addresses with house numbers, street names, city, state, pincode
- Partial addresses with just city, state, and pincode
- Even just city and state combinations
- Addresses from contact information sections
```

### 3. **Fallback Address Extraction**
Added `fallback_address_extraction()` function that uses pattern matching when AI fails:

```python
def fallback_address_extraction(resume_text: str) -> dict:
    # Pattern-based extraction using:
    # - Address keywords detection
    # - Indian city names recognition
    # - Pincode pattern matching
    # - Context-aware line grouping
```

### 4. **Field Mapping Consistency**
Added field mapping in `views.py`:

```python
# Ensure field consistency
if parsed_data.get("address") and not parsed_data.get("residential_address"):
    parsed_data["residential_address"] = parsed_data["address"]
elif parsed_data.get("residential_address") and not parsed_data.get("address"):
    parsed_data["address"] = parsed_data["residential_address"]
```

### 5. **Intelligent City Extraction**
Added city extraction from addresses for better pincode lookup:

```python
# Extract city from address for pincode lookup
indian_cities = [
    "mumbai", "delhi", "bangalore", "chennai", "kolkata", "pune", 
    "hyderabad", "ahmedabad", "jaipur", "surat", ...
]
for city in indian_cities:
    if city in address_lower:
        parsed_data["city"] = city.title()
        break
```

---

## 🎯 Expected Improvements

### Before Fix:
- ❌ "Mumbai, Maharashtra" → Rejected (no street keywords)
- ❌ "Bangalore 560001" → Rejected (no street keywords)  
- ❌ "Sector 18, Noida" → Rejected (inconsistent field mapping)
- ❌ AI misses address → No fallback mechanism

### After Fix:
- ✅ "Mumbai, Maharashtra" → Accepted (has Indian location)
- ✅ "Bangalore 560001" → Accepted (has digits + location)
- ✅ "Sector 18, Noida" → Accepted (has keywords + proper mapping)
- ✅ AI misses address → Fallback pattern matching kicks in

---

## 🧪 Testing

Run the test script to verify improvements:

```bash
python test_address_extraction.py
```

This will test various address formats:
1. Complete addresses with street details
2. City and pincode combinations
3. Partial addresses with keywords
4. Minimal location information
5. Mumbai-style pincode formats

---

## 📋 Summary of Changes

### Files Modified:
1. **`ai_extractor.py`**:
   - Enhanced address validation logic
   - Added fallback extraction function
   - Improved AI prompt for better address recognition
   - Fixed field name to `residential_address`

2. **`views.py`**:
   - Added field mapping consistency checks
   - Added intelligent city extraction
   - Improved pincode lookup logic

3. **Test Files**:
   - `test_address_extraction.py` - Demonstration script
   - `ADDRESS_EXTRACTION_FIXES.md` - This documentation

### Key Benefits:
- **Higher Success Rate**: More addresses will be captured successfully
- **Better Data Quality**: Consistent field mapping prevents data loss
- **Robust Fallback**: Pattern matching when AI fails
- **Indian Context**: Better handling of Indian address formats
- **Flexible Validation**: Accepts partial but valid address information

The address extraction should now work significantly better across different resume formats and address styles!
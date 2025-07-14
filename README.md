# strategy-
I was thinking of asking a person whether their image is in PC-written format to save money by using local OCR for documents that are likely clean and easy to recognize. Since local OCR is free and performs well on typed text, this approach avoids unnecessary API calls and reduces costs.

If the user indicates that the image is handwritten, the script skips local OCR and directly uses the OpenAI Vision API, which is more accurate but also more expensive. For cases where the user is unsure, the system defaults to trying local OCR first and only falls back to OpenAI Vision if the result doesn't contain key information (like name, date, or amount).

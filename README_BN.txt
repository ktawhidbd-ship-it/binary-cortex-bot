বাইনারি Cortex Bot — ১ মিনিটের মার্কেট অ্যানালাইসিস

এই প্যাকেজে আছে:
- FastAPI ভিত্তিক API সার্ভার
- /health : সার্ভার চালু আছে কি না পরীক্ষা
- /analyze : ১ মিনিটের OHLC ক্যান্ডেল পাঠালে CALL / PUT / WAIT বিশ্লেষণ
- Render hosting-এর জন্য render.yaml

গুরুত্বপূর্ণ:
১) এই বট নিজে থেকে লাইভ মার্কেট ডেটা সংগ্রহ করে না।
২) Cortex বা অন্য ডেটা-সোর্স থেকে সাম্প্রতিক অন্তত ৩০টি ১-মিনিটের ক্যান্ডেল /analyze এ পাঠাতে হবে।
৩) Cortex-এ যুক্ত করার আগে Cortex-এর API/Webhook বা custom endpoint কীভাবে নেয় তা যাচাই করতে হবে।
৪) CALL/PUT কোনো নিশ্চয়তাপূর্ণ ট্রেডিং নির্দেশনা নয়। আগে ডেমোতে পরীক্ষা করুন।

Render-এ হোস্ট:
1. ZIP Extract করে ফাইলগুলো GitHub repository-তে আপলোড করুন।
2. Render-এ New + > Web Service নির্বাচন করুন।
3. GitHub repository connect করুন।
4. Build Command: pip install -r requirements.txt
5. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
6. Deploy করুন। সফল হলে https://...onrender.com URL পাবেন।
7. URL-এর শেষে /health যোগ করে পরীক্ষা করুন। {"ok":true} এলে সার্ভার চলছে।

API ব্যবহার:
POST https://YOUR-SERVICE.onrender.com/analyze
Content-Type: application/json

{
  "symbol": "EURUSD",
  "timeframe": "1m",
  "candles": [
    {"open":1.1000,"high":1.1010,"low":1.0990,"close":1.1005},
    ... অন্তত ৩০টি ক্যান্ডেল ...
  ]
}

প্রতিটি ক্যান্ডেলের open, high, low, close দিতে হবে।

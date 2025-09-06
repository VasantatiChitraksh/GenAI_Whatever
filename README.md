# GenAI_Whatever

### Installation steps
1. sudo apt update
2. git clone https://github.com/VasantatiChitraksh/GenAI_Whatever.git
3. cd GenAI_Whatever/vishwas-ai
4. gcloud auth login
5. gcloud config set project YOUR_GCP_PROJECT_ID - look for it in the code, strictly within the team
6. cd services/core-engine
7. python3 -m venv venv
8. source venv/bin/activate
9. gcloud auth application-default login
10. pip install -r requirements.txt
11. In the venv, n the services/core-engine run: flask --app main run 
12. In a new terminal, run the following command - api testing
```
curl -X POST [http://127.0.0.1:5000/verify](http://127.0.0.1:5000/verify) \
-H "Content-Type: application/json" \
-d '{
  "text": "Your test text here",
  "image_url": "[https://your.image.url/here.jpg](https://your.image.url/here.jpg)"
}'
```
13. 
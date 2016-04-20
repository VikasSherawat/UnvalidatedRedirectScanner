rm output/*.json
rm logs/*.log
echo "---------------------------------------------------"
echo "Unvalidated Redirect scanner started"
echo "---------------------------------------------------"
echo "Phase1- Crawling started"
scrapy crawl app
echo "Phase1- ended. check the Output file for possible injection points"
echo "---------------------------------------------------"
echo "Phase2- Generating Payload"
python phase2.py
echo "Phase2 is ended. Payloads file is generated"
echo "---------------------------------------------------"
echo "Phase3- Injecting payload"
python phase3.py
echo "Phase3 is ended. Check the output file for bugs found"
echo "---------------------------------------------------"
echo "Phase4- Verifying reported bugs"
python phase4.py
echo "---------------------------------------------------"
echo "Phase4 is ended."
echo "***************************************************"
echo "Scanning is completed."
echo "***************************************************"

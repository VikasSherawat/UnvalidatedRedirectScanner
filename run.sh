echo "---------------------------------------------------"
echo "Unvalidated Redirect scanner started"
echo "---------------------------------------------------"
echo "Phase1- Crawling started"
scrapy crawl app2
echo "Phase1- ended. check the Output file"
echo "---------------------------------------------------"
echo "Phase2- Generating Payload startedf"
python phase2.py
echo "Phase2 is ended. Payloads are generated"
echo "---------------------------------------------------"
echo "Phase3- Payload injetions started"
python phase3.py
echo "Phase3 is ended. Check the output file for bugs"
echo "---------------------------------------------------"
echo "Phase4- Verifying reported bugs started"
python phase4.py
echo "Phase4 is ended. Output file is generated"
echo "---------------------------------------------------"
echo "***************************************************"
echo "Scanning is completed."
echo "***************************************************"

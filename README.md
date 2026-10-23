Checkpoint 3 Team T07

Regional Logistics variant A2
Section 2

Assigned call
cp34_instance(7, 'A', 2)

All eight packet checks match
41 points
14 centers
Capacity 82
Total demand 903
13 premium points
Sum of point distances rounded to three decimals 87717.651
1735 variables
1805 constraint rows excluding bounds

Main results
LP value 1183.039977
76 fractional binary columns consisting of 63 assignments and 13 center openings
All premium points are served and the penalty term is zero
All five KKT errors are below 1e-6
A5 price 34.306927747
Both sensitivity slopes agree with the price within 1e-6

Four student allocation

Igor Makowski M1
Own src/model and tests/test_M1.py
Review and complete S1 and H1

Bek Marat M2
Own src/lp and tests/test_M2.py
Review and complete S2 and H2

Timur Ryabov M3
Own src/kkt and tests/test_M3.py
Review and complete S3 and H3

Sofiya Akhmadishina M4
Own src/sens and tests/test_M4.py
Review and complete S4 and H4

All four share Task 5 S5 H5 Synthesis experiments/run_all.py and assembly
The planned workload is 25 percent each
Record actual completed work and percentages before signing
The assignments describe responsibility for review and completion
They do not establish individual authorship of this AI generated draft

Reproduce the numerical results

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m experiments.run_all
python -m pytest -q --disable-warnings

On Windows activate the environment with .venv\Scripts\activate
Use python instead of python3 when creating the environment on Windows

The mandatory command python -m experiments.run_all writes Tables 1 to 3
It stops if a packet check or optimality condition fails
The results directory includes all variable values row prices certificates and checksums
Solve time measures the LP solve including interface preparation and varies by machine

Edit and rebuild the report

python -m pip install -r requirements-report.txt
python -m experiments.build_report

This creates report/T07_Checkpoint3.docx and report/T07_Checkpoint3.txt
Open the DOCX in Word or LibreOffice and export it to T07_Checkpoint3.pdf
The supplied PDF was rendered and visually checked
The main report is six pages then H1 to H5 and the contribution page
Every paragraph uses plain black text
All report claims refer to the T07 A2 data

Before final export enter repository_url and commit_hash in team_config.json
The report builder reads these fields directly
Leave these metadata edits out of the numerical calculations
Add genuine signatures to the analysis pages hand task pages and contribution page
Each member must complete their own hand work and role review

Files for the existing private Checkpoint 2 repository

src/model contains the unchanged public generator and sparse reference matrix
src/lp solves the LP and calibrates price signs
src/kkt checks plain primal and dual vectors without a solver result object
src/sens changes only the designated right hand side and checks the price interval
src/triangle.py evaluates the five triangle tasks
experiments/run_all.py regenerates the numerical results
experiments/build_report.py creates the plain report
tests/test_M1.py through test_M5.py reproduce the triangle calculations
tests/test_reference_models.py checks all six reference variants and an independent CBC certificate
tests/test_T07.py compares the assigned model with an independent CBC solve
results contains CSV files full solution vectors and the analysis record
report files are generated locally by experiments/build_report.py
The submitted PDF should name the code commit that produced its results

Submission

Repository https://github.com/Wezzeso/T07
This private repository was created at the user request for the T07 work
The previous Checkpoint 2 repository and its history were not supplied
If the course requires that history the team should arrange its transfer or confirm the new repository with the instructor
Review the uploaded files before submission
Each person commits only work they actually performed and can explain
Use the required prefixes [Model] [LP] [KKT] [Sens] and [Report]
After the final real commit obtain the hash with git rev-parse HEAD
Put the repository URL and that hash on the report cover
Upload one signed PDF named T07_Checkpoint3.pdf
Tag the final real commit checkpoint3 and push that tag
Do not submit an unsigned copy as complete
If nobody has the old repository link ask a teammate or the instructor for it
No member signatures or teammate authorship were invented

Declarations

OpenAI Codex generated and adapted this code report draft tests and hand task worked solutions
The earlier local example implementation was reused and adapted to the actual T07 packet
AI assistance must remain declared after member review
The mathematical reference model is from the supplied Checkpoint 3 instructions
The assigned data and triangle numbers are from the private T07 A2 packet
The public generator was copied unchanged from the file supplied by the user
Numerical work uses NumPy SciPy and PuLP below version 4
Pytest runs verification and python-docx builds the editable report
No other team's private solution or private reference objective was used
Signatures and individual code authorship must reflect the members' actual work

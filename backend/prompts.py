format_prompt = '''
    Extract the following details from the CV:
    - Candidate Name
    - Total Years of Experience
    - Last Job Title
    - Highest Education Level
    - Any Professional Certificates
    - Any Gaps in Employment

    CV Text:
    {input}

    Please return the result as JSON with keys: name, experience, last_job, education, certificates, gaps.
'''
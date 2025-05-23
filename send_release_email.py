import os
import smtplib
import subprocess
import re
from email.message import EmailMessage
from docx import Document

# 🔹 Get the latest release tag or initialize to v1.0.0
def get_latest_release_tag():
    try:
        tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0']).strip().decode()
        return tag
    except subprocess.CalledProcessError:
        return "v1.0.0"

# 🔹 Increment patch version
def increment_version(tag):
    match = re.match(r"v(\d+)\.(\d+)\.(\d+)", tag)
    if match:
        major, minor, patch = map(int, match.groups())
        patch += 1
        return f"v{major}.{minor}.{patch}"
    return "v1.0.0"

# 🔹 Tag the new release and push it
def tag_and_push(tag):
    try:
        subprocess.run(['git', 'tag', tag], check=True)
        subprocess.run(['git', 'push', 'origin', tag], check=True)
        print(f"✅ Created and pushed tag: {tag}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to tag or push: {e}")

# 🔹 Read content from .docx file
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# 🔹 Send email with release note
def send_email_with_release(tag, content, docx_path):
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")

    msg = EmailMessage()
    msg['Subject'] = f'📦 Website Release Note - Version {tag}'
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(content)

    with open(docx_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(f.name)
        msg.add_attachment(file_data, maintype='application',
                           subtype='vnd.openxmlformats-officedocument.wordprocessingml.document',
                           filename=file_name)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Email failed: {e}")

# 🔹 Main execution
if __name__ == "__main__":
    docx_file_path = "Website_Release_Note.docx"
    latest_tag = get_latest_release_tag()
    new_tag = increment_version(latest_tag)
    tag_and_push(new_tag)
    content = read_docx(docx_file_path)
    send_email_with_release(new_tag, content, docx_file_path)

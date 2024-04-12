import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pdfkit  # Make sure to install this library
from PyPDF2 import PdfFileMerger
import fitz
import sys
def download_page(url, folder_path, visited_urls=set()):
    if url in visited_urls:
        return
    else:
        visited_urls.add(url)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        })
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        html_content = response.content.decode('utf-8')
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to {url}: {e}")
        return
        #html_content = None

    # Continue with your program, using 'html_content' if it's not None

    # Try decoding content using the detected encoding
    content = response.content
    encoding = response.encoding if response.encoding is not None else 'utf-8'
    decoded_content = content.decode(encoding, errors='replace')

    try:
        soup = BeautifulSoup(decoded_content, "html.parser")  # Or "lxml" or "html5lib"
        
        for style_tag in soup.find_all('style'):
            style_tag.decompose()

        for iframe_tag in soup.find_all('iframe'):
            iframe_tag.decompose()

        for script_tag in soup.find_all('script'):
            script_tag.decompose()

    except Exception as e:
        print(f"Failed to parse {url}: {e}")
        return    
    
    #print(decoded_content)

    file_name = urlparse(url).path.split("/")[-1] or "index"
    base_pdf_file_name = file_name.replace('.htm', '').replace('.html', '').replace('.aspx', '').replace('.php', '')
    pdf_file_name = os.path.join(folder_path, f"{base_pdf_file_name}.pdf")

    # Ensure the file name is unique
    counter = 1
    while os.path.exists(pdf_file_name):
        pdf_file_name = os.path.join(folder_path, f"{base_pdf_file_name}_{counter}.pdf")
        counter += 1

    # Set the path to wkhtmltopdf executable file
    path_wkhtmltopdf = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe' 
    options = {
        'enable-local-file-access': None,
        'encoding': "UTF-8",
        'custom-header' : [
            ('Accept-Encoding', 'gzip')
        ],
        'no-images': '',
        'disable-external-links': '',
        'quiet': '',
        'grayscale':'',
        'log-level': 'error',
        'lowquality':'',
    }
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    # Add options for encoding and other potential issues
    
    #print(type(pdfkit))

    try:    
        pdfkit.from_string(str(soup), pdf_file_name, configuration=config, options = options)

        print(f"Saved: {pdf_file_name} Connected to {url}")
        # Convert PDF to grayscale
        #convert_to_grayscale(pdf_file_name)

    except Exception as e:

        print(f"Failed to convert {url} to PDF: {e}")
        #convert_to_grayscale(pdf_file_name)
    
    # Parse page content to find hyperlinks
    links = soup.find_all("a", href=True)
    base_domain = urlparse(url).netloc

    for link in links:
        href = link["href"]
        if not href.startswith("http"):
            linked_url = urljoin(url, href)
        else:
            linked_url = href

        # Skip downloading non-text files
        if linked_url.split('?')[0].endswith(('.pdf','.csv', '.rar', '.zip', '.exe', '.doc', '.docx','.jpg','.png','.tiff','.ppt','.xls','.xlsx')):
            continue

        if urlparse(linked_url).netloc == base_domain and linked_url not in visited_urls:
            download_page(linked_url, folder_path, visited_urls)



def merge_to_single_pdf(folder_path):
    # Get all PDF files in the specified folder
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return

    # Sort the files based on their names (this might need modification based on your needs)
    pdf_files.sort()

    # Generate single PDF file path
    merged_pdf_file_path = os.path.join(folder_path, "merged_output.pdf")

    # Merge PDF files into one
    merger = PdfFileMerger()

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(folder_path, pdf_file)
        try:
            merger.append(pdf_file_path)
        except Exception as e:
            print(f"Error reading PDF file '{pdf_file}': {e}")
            continue

    merger.write(merged_pdf_file_path)
    merger.close()

    print(f"Single PDF file created successfully: {merged_pdf_file_path}")

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(folder_path, pdf_file)
        if pdf_file_path != merged_pdf_file_path:
            os.remove(pdf_file_path)
            print(f"Deleted file: {pdf_file_path}")


def convert_pdf_to_txt(pdf_path, txt_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
    
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)



def main():
    if len(sys.argv) != 3:
        print("Usage: python your_script.py <url> <folder_path>")
        sys.exit(1)

    url = sys.argv[1]
    folder_path = sys.argv[2]

    download_page(url, folder_path)
    merge_to_single_pdf(folder_path)

if __name__ == "__main__":
    main()


#downloader 的內容
import argparse
import sys
import uuid

if 'src' not in sys.path:
    sys.path.append('src')

from src.function_client import get_data_h2ogpt


def has_gpu():
    import subprocess
    try:
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def pdf_has_images(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        if image_list:
            # print(f"Page {page_num + 1} contains {len(image_list)} image(s)")
            return True
    # print("No images found in the PDF")
    return False


def get_num_pages(file):
    try:
        import fitz
        src = fitz.open(file)
        return len(src)
    except:
        return None


def process_files(files, urls):
    text_context_list = []

    textual_types = ('.txt', '.csv', '.toml', '.py', '.rst', '.rtf', '.md', '.html', '.htm', '.xml', '.json', '.yaml',
                     '.yml', '.ini', '.log', '.tex', '.sql', '.sh', '.bat', '.js', '.css', '.php', '.jsp', '.pl', '.r',
                     '.lua', '.conf', '.properties', '.tsv', '.xhtml', '.srt', '.vtt', '.cpp', '.c', '.h', '.go')

    doc_types = ('.pdf', '.docx', '.doc', '.epub', '.pptx', '.ppt', '.xls', '.xlsx')

    from openai_server.agent_tools.common.utils import filename_is_url
    files_new = []
    urls_new = []
    for filename in files + urls:
        if filename in files:
            if filename_is_url(filename):
                urls_new.append(filename)
            else:
                files_new.append(filename)
        else:
            urls_new.append(filename)

    files = files_new
    urls = urls_new

    for filename in files + urls:
        if filename.lower().endswith('.pdf'):
            if filename in urls:
                from openai_server.agent_tools.common.utils import download_simple
                newfile = download_simple(filename)
                num_pages = get_num_pages(newfile)
                has_images = pdf_has_images(newfile)
            else:
                num_pages = get_num_pages(filename)
                has_images = pdf_has_images(filename)
            if num_pages and num_pages < 20:
                if has_images:
                    enable_pdf_doctr = 'on'
                    use_pypdf = 'off'
                else:
                    enable_pdf_doctr = 'off'
                    use_pypdf = 'on'
                use_pymupdf = 'off'
            else:
                enable_pdf_doctr = 'off'
                use_pymupdf = 'on'
                use_pypdf = 'off'
        else:
            # pymupdf faster for many pages
            enable_pdf_doctr = 'off'
            use_pymupdf = 'on'
            use_pypdf = 'off'

        sources1, known_type = get_data_h2ogpt(filename,
                                               is_url=filename in urls,
                                               verbose=False,
                                               use_pymupdf=use_pymupdf,
                                               use_pypdf=use_pypdf,
                                               use_unstructured_pdf='off',
                                               enable_pdf_ocr='off',
                                               enable_pdf_doctr=enable_pdf_doctr,
                                               try_pdf_as_html='off',
                                               enable_captions=False,
                                               enable_llava=False,
                                               chunk=False,
                                               enable_transcriptions=False,
                                               )
        pages1 = [x.page_content for x in sources1]
        all_content1 = "\n\n".join(pages1)

        if filename.lower().endswith('.pdf') and enable_pdf_doctr == 'off':
            if use_pymupdf == 'on':
                use_pymupdf = 'off'
                use_pypdf = 'on'
            else:
                use_pymupdf = 'on'
                use_pypdf = 'off'
            sources2, known_type = get_data_h2ogpt(filename,
                                               is_url=filename in urls,
                                               verbose=False,
                                               use_pymupdf=use_pymupdf,
                                               use_pypdf=use_pypdf,
                                               use_unstructured_pdf='off',
                                               enable_pdf_ocr='off',
                                               enable_pdf_doctr=enable_pdf_doctr,
                                               try_pdf_as_html='off',
                                               enable_captions=False,
                                               enable_llava=False,
                                               chunk=False,
                                               enable_transcriptions=False,
                                               )

            pages2 = [x.page_content for x in sources1]
            all_content2 = "\n\n".join(pages2)

            # choose one with more content in case pymupdf fails to find info
            if len(all_content2) > len(all_content1):
                sources1 = sources2

        if not sources1:
            print(f"Unable to handle file type for {filename}")
        else:
            text_context_list.extend([x.page_content for x in sources1])

    return text_context_list


def get_text(files, urls):
    text_context_list = process_files(files, urls)

    # Join the text_context_list into a single string
    output_text = "\n\n".join(text_context_list)

    return output_text


def main():
    parser = argparse.ArgumentParser(description="Converts document to text")
    parser.add_argument("--files", nargs="+", required=False, help="Files to convert to text")
    parser.add_argument("--urls", nargs="+", required=False, help="URLs to convert to text")
    parser.add_argument("--output", type=str, required=False, help="Output filename")
    args = parser.parse_args()

    if not args.output:
        args.output = f"conversion_to_text_{str(uuid.uuid4())[:6]}.txt"

    files = args.files or []
    urls = args.urls or []

    output_text = get_text(files, urls)

    # Write the output to the specified file
    with open(args.output, "w") as f:
        f.write(output_text)

    print(f"{files + urls} have been converted to text and written to {args.output}")
    print("The output may be complex for input of PDFs or URLs etc., so do not assume the structure of the output file and instead check it directly.")
    print("Probably a verify any use of convert_document_to_text.py with ask_question_about_documents.py")

    max_tokens = 1024
    max_chars = max_tokens * 4
    if len(output_text) > max_chars:
        print("Head of the output:")
        print(output_text[:max_chars])
    else:
        print(output_text)

    return output_text


if __name__ == "__main__":
    main()


"""
Examples:

wget https://aiindex.stanford.edu/wp-content/uploads/2024/04/HAI_2024_AI-Index-Report.pdf
python /home/jon/h2ogpt/openai_server/agent_tools/convert_document_to_text.py --urls http://www.cnn.com
python /home/jon/h2ogpt/openai_server/agent_tools/convert_document_to_text.py --files HAI_2024_AI-Index-Report.pdf
python /home/jon/h2ogpt/openai_server/agent_tools/convert_document_to_text.py --urls https://aiindex.stanford.edu/wp-content/uploads/2024/04/HAI_2024_AI-Index-Report.pdf
"""
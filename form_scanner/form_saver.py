from fpdf import FPDF

def save_form_batch(im_files_list:list, target_name):
    pdf = FPDF()
    for im_file in im_files_list:
        pdf.add_page()
        pdf.image(im_file, x = 0, y = 0, w = 210)

    pdf.output(target_name, 'F')
    return

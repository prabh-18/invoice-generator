import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
import helpers
import pdf_generator
import email_sender

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Invoice Generator")
        self.root.geometry("650x850")
        
        # Data storage
        self.logo_path = tk.StringVar()
        self.config = helpers.load_config()
        
        self.create_widgets()
        self.load_defaults()

    def create_widgets(self):
        # Configure styles
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#1a1a2e")
        style.configure("Section.TLabelframe.Label", font=("Helvetica", 10, "bold"), foreground="#1a1a2e")
        style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=10)

        # Main Scrollable Canvas (if needed, but for now just a frame with padding)
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="20")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- HEADER ---
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, text="Professional Invoice Generator", style="Header.TLabel").pack(side=tk.LEFT)

        # --- BUSINESS SECTION ---
        biz_frame = ttk.LabelFrame(scrollable_frame, text=" Business Information ", padding=15)
        biz_frame.pack(fill=tk.X, pady=10)

        self._add_row(biz_frame, 0, "Business Name:", "biz_name_entry")
        self._add_row(biz_frame, 1, "Address:", "biz_addr_entry")
        self._add_row(biz_frame, 2, "Email:", "biz_email_entry")
        self._add_row(biz_frame, 3, "Phone:", "biz_phone_entry")
        self._add_row(biz_frame, 4, "GSTIN (15 chars):", "biz_gstin_entry")

        # Logo Row
        ttk.Label(biz_frame, text="Business Logo:").grid(row=5, column=0, sticky=tk.W, pady=5)
        logo_btn_frame = ttk.Frame(biz_frame)
        logo_btn_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Button(logo_btn_frame, text="Upload Logo", command=self.select_logo).pack(side=tk.LEFT)
        self.logo_label = ttk.Label(logo_btn_frame, text="No logo selected", foreground="gray", padding=(10, 0))
        self.logo_label.pack(side=tk.LEFT)

        # --- CLIENT SECTION ---
        client_frame = ttk.LabelFrame(scrollable_frame, text=" Client Details ", padding=15)
        client_frame.pack(fill=tk.X, pady=10)

        self._add_row(client_frame, 0, "Client Name:", "client_name_entry")
        self._add_row(client_frame, 1, "Client Email:", "client_email_entry")

        # --- INVOICE & SERVICE SECTION ---
        service_frame = ttk.LabelFrame(scrollable_frame, text=" Invoice & Service ", padding=15)
        service_frame.pack(fill=tk.X, pady=10)

        self._add_row(service_frame, 0, "Description:", "desc_entry")
        self._add_row(service_frame, 1, "Amount (EXCL Tax):", "amount_entry")
        
        # GST Toggle
        self.gst_applicable = tk.BooleanVar(value=True)
        self.gst_check = ttk.Checkbutton(service_frame, text="GST Applicable", variable=self.gst_applicable, command=self.toggle_gst_fields)
        self.gst_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Tax Fields (Wrappers for visibility toggle)
        self.tax_fields_frame = ttk.Frame(service_frame)
        self.tax_fields_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(self.tax_fields_frame, text="CGST %:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cgst_entry = ttk.Entry(self.tax_fields_frame, width=15)
        self.cgst_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        self.cgst_entry.insert(0, "9.0")

        ttk.Label(self.tax_fields_frame, text="SGST %:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sgst_entry = ttk.Entry(self.tax_fields_frame, width=15)
        self.sgst_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)
        self.sgst_entry.insert(0, "9.0")

        # Dates
        self._add_row(service_frame, 4, "Invoice Date:", "inv_date_entry", width=25)
        self.inv_date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self._add_row(service_frame, 5, "Due Date:", "due_date_entry", width=25)

        # --- PAYMENT SECTION ---
        bank_frame = ttk.LabelFrame(scrollable_frame, text=" Payment Details ", padding=15)
        bank_frame.pack(fill=tk.X, pady=10)

        self._add_row(bank_frame, 0, "UPI ID:", "upi_entry")
        self._add_row(bank_frame, 1, "Account No:", "acc_entry")
        self._add_row(bank_frame, 2, "IFSC Code:", "ifsc_entry")

        # --- ACTIONS ---
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, pady=30)
        
        generate_btn = ttk.Button(btn_frame, text=" GENERATE PDF INVOICE ", style="Action.TButton", command=self.generate_invoice)
        generate_btn.pack(side=tk.BOTTOM, fill=tk.X)

    def _add_row(self, parent, row, label_text, attr_name, width=45):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        setattr(self, attr_name, entry)

    def toggle_gst_fields(self):
        if self.gst_applicable.get():
            self.tax_fields_frame.grid()
        else:
            self.tax_fields_frame.grid_remove()

    def select_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.logo_path.set(file_path)
            self.logo_label.config(text=os.path.basename(file_path), foreground="#2e7d32")

    def load_defaults(self):
        """Pre-fill business and bank entries from config."""
        if self.config:
            self.biz_name_entry.insert(0, self.config.get('business_name', ''))
            self.biz_addr_entry.insert(0, self.config.get('business_address', ''))
            self.biz_email_entry.insert(0, self.config.get('business_email', ''))
            self.biz_phone_entry.insert(0, self.config.get('business_phone', ''))
            self.biz_gstin_entry.insert(0, self.config.get('business_gstin', ''))
            self.upi_entry.insert(0, self.config.get('upi_id', ''))
            self.acc_entry.insert(0, self.config.get('account_no', ''))
            self.ifsc_entry.insert(0, self.config.get('ifsc_code', ''))
            
            if self.config.get('logo_path') and os.path.exists(self.config['logo_path']):
                self.logo_path.set(self.config['logo_path'])
                self.logo_label.config(text=os.path.basename(self.config['logo_path']), foreground="#2e7d32")

    def generate_invoice(self):
        # 1. Capture Inputs
        data = {
            "business_name": self.biz_name_entry.get().strip(),
            "business_address": self.biz_addr_entry.get().strip(),
            "business_email": self.biz_email_entry.get().strip(),
            "business_phone": self.biz_phone_entry.get().strip(),
            "business_gstin": self.biz_gstin_entry.get().strip(),
            "logo_path": self.logo_path.get(),
            "client_name": self.client_name_entry.get().strip(),
            "client_email": self.client_email_entry.get().strip(),
            "description": self.desc_entry.get().strip(),
            "amount": self.amount_entry.get().strip(),
            "gst_applicable": self.gst_applicable.get(),
            "cgst_rate": self.cgst_entry.get().strip() if self.gst_applicable.get() else "0",
            "sgst_rate": self.sgst_entry.get().strip() if self.gst_applicable.get() else "0",
            "invoice_date": self.inv_date_entry.get().strip(),
            "due_date": self.due_date_entry.get().strip(),
            "upi_id": self.upi_entry.get().strip(),
            "account_no": self.acc_entry.get().strip(),
            "ifsc_code": self.ifsc_entry.get().strip(),
        }

        # 2. Validation
        if not all([data['business_name'], data['client_name'], data['description'], data['amount']]):
            messagebox.showerror("Error", "Required fields (Business, Client, Description, Amount) are missing!")
            return

        if not helpers.is_numeric(data['amount']):
            messagebox.showerror("Error", "Amount must be a numeric value.")
            return

        # 3. Calculations
        data['amount'] = float(data['amount'])
        data['cgst_rate'] = float(data['cgst_rate'] or 0)
        data['sgst_rate'] = float(data['sgst_rate'] or 0)
        
        tax_results = helpers.calculate_taxes(data['amount'], data['cgst_rate'], data['sgst_rate'])
        data['cgst_amount'] = tax_results['cgst'] if data['gst_applicable'] else 0
        data['sgst_amount'] = tax_results['sgst'] if data['gst_applicable'] else 0
        data['total_payable'] = tax_results['total'] if data['gst_applicable'] else data['amount']
        
        # 4. Save config for next time
        self.config.update({
            "business_name": data['business_name'],
            "business_address": data['business_address'],
            "business_email": data['business_email'],
            "business_phone": data['business_phone'],
            "business_gstin": data['business_gstin'],
            "upi_id": data['upi_id'],
            "account_no": data['account_no'],
            "ifsc_code": data['ifsc_code'],
            "logo_path": data['logo_path']
        })
        helpers.save_config(self.config)

        # 5. Generate PDF
        data['invoice_number'] = helpers.get_next_invoice_number()
        
        output_filename = f"Invoice_{data['invoice_number']}_{data['client_name'].replace(' ', '_')}.pdf"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        
        try:
            pdf_generator.generate_invoice_pdf(data, output_path)
            messagebox.showinfo("Success", f"Invoice generated successfully!\n\nSaved at: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
            return

        # ── Ask user if they want to send the invoice via email ───────────────
        send_email = messagebox.askyesno(
            "Send Invoice via Email",
            f"Send invoice to {data['client_name']} via email?\n\n"
            f"Recipient: {data.get('client_email', 'N/A')}"
        )

        if send_email:
            success, message = email_sender.send_invoice_email(
                config=self.config,
                invoice_data=data,
                pdf_path=output_path
            )
            if success:
                print(message)  # Print to terminal as requested
                messagebox.showinfo("Email Sent", message)
            else:
                print(f"Email failed: {message}")
                messagebox.showerror("Email Failed", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()

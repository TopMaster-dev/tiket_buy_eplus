import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import sys
import io

class TicketBuyerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket Buyer - E+ Automation")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar(value="https://eplus.jp")
        self.is_running = False
        self.browser_process = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="E+ Ticket Buyer Automation", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        url_label = ttk.Label(main_frame, text="URL:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=2, sticky=tk.E, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="START", command=self.start_automation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="STOP", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to start", font=("Arial", 10))
        self.status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        # Log output
        log_label = ttk.Label(main_frame, text="Log Output:")
        log_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.log_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Waiting...")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_automation(self):
        """Start the automation in a separate thread"""
        if self.is_running:
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Automation running...")
        self.progress_var.set("Starting browser...")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        self.log_message("Starting automation...")
        
        # Run automation in separate thread
        self.automation_thread = threading.Thread(target=self.run_automation_async, args=(url,))
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def stop_automation(self):
        """Stop the automation"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopping automation...")
        self.progress_var.set("Stopping...")
        self.log_message("Stopping automation...")
        
    async def run_at_Date(self, page):
        """Modified run_at_Date function with GUI logging"""
        has_run_today = False

        while self.is_running:
            now = datetime.now()

            if now.hour == 12 and now.minute == 0 and not has_run_today:
                self.log_message(f"🟢 It's {now} AM! Running function...")
                self.progress_var.set(f"Executing at {now}")
                
                try:
                    await page.wait_for_selector("div.bt-area span#enter-bt-zumi a", timeout=10000)
                    await page.click("div.bt-area span#enter-bt-zumi a")
                    self.log_message('Clicked: div.bt-area span#enter-bt-zumi a')
                    
                    await page.wait_for_selector('div.accept-con input#i14', timeout=10000)
                    await page.click('div.accept-con input#i14')
                    self.log_message('Clicked: div.accept-con input#i14')
                    
                    await page.wait_for_selector('div.con input#i8', timeout=10000)
                    await page.click('div.con input#i8')
                    self.log_message('Clicked: div.con input#i8')
                    
                    await page.wait_for_selector('div.cont-block span.enter-bt span a', timeout=10000)
                    await page.click('div.cont-block span.enter-bt span a')
                    self.log_message(f"✅ Done Date:{now}")
                    has_run_today = True
                    return False
                except Exception as e:
                    self.log_message(f"❌ Error during execution: {str(e)}")
                    return False
                    
            if not self.is_running:
                break
                
            self.log_message(f"Date:{now}")
            # Reset flag after 10 AM
            if now.hour > 10:
                has_run_today = False
            await asyncio.sleep(0.1)  # Check every 10 seconds

    async def run_automation(self, url):
        """Main automation function"""
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        
        try:
            async with async_playwright() as p:
                self.log_message("Launching browser...")
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(user_agent=user_agent)
                page = await context.new_page()

                # Avoid automation detection
                await page.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")

                self.log_message("Navigating to URL...")
                self.progress_var.set("Loading page...")
                await page.goto(url, wait_until="load", timeout=300000)
                self.log_message("Page loaded successfully")
                self.progress_var.set("Waiting for buy...")
                
                await self.run_at_Date(page)
                
                if self.is_running:
                    self.log_message("Finished scraping. Browser will stay open.")
                    await asyncio.sleep(30)  # Keep browser open for 30 seconds
                    
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        finally:
            if self.is_running:
                self.root.after(0, self.automation_finished)
    
    def run_automation_async(self, url):
        """Run automation in asyncio event loop"""
        asyncio.run(self.run_automation(url))
    
    def automation_finished(self):
        """Called when automation finishes"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Automation finished")
        self.progress_var.set("Finished")
        self.log_message("Automation finished")

def main():
    root = tk.Tk()
    app = TicketBuyerGUI(root)
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Make the start button more prominent
    style.configure("Accent.TButton", 
                   background="#0078d4", 
                   foreground="white",
                   font=("Arial", 10, "bold"))
    
    root.mainloop()

if __name__ == "__main__":
    main() 

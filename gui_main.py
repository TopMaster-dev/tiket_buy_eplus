import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

class TicketBuyerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("チケット購入 - E+自動化")
        self.root.geometry("600x550")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar(value="https://eplus.jp")
        self.time_var = tk.StringVar(value="10:00:00.000")
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
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="E+ チケット購入自動化", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        url_label = ttk.Label(main_frame, text="URL:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=80)
        url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=10)
        
        # Time input
        time_label = ttk.Label(main_frame, text="時間 (HH:MM:SS.mmm):")
        time_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        time_entry = ttk.Entry(main_frame, textvariable=self.time_var, width=20)
        time_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 10), pady=10)
        
        # Help text for time format
        time_help = ttk.Label(main_frame, text="形式: HH:MM:SS.mmm (24時間制)", font=("Arial", 8), foreground="gray")
        time_help.grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=3, sticky=tk.E, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="開始", command=self.start_automation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="準備完了", font=("Arial", 10))
        self.status_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))
        
        # Log output
        log_label = ttk.Label(main_frame, text="ログ出力:")
        log_label.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.log_text.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="待機中...")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=6, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
    def validate_time_format(self, time_str):
        """Validate time format HH:MM:SS.mmm or HH:MM"""
        try:
            # Check if it's the old format (HH:MM)
            if ':' in time_str and time_str.count(':') == 1:
                hour, minute = map(int, time_str.split(':'))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return True
            # Check if it's the new format (HH:MM:SS.mmm)
            elif ':' in time_str and time_str.count(':') == 2:
                time_part, millisecond_part = time_str.split('.')
                hour, minute, second = map(int, time_part.split(':'))
                millisecond = int(millisecond_part) if millisecond_part else 0
                if (0 <= hour <= 23 and 0 <= minute <= 59 and 
                    0 <= second <= 59 and 0 <= millisecond <= 999):
                    return True
        except (ValueError, AttributeError):
            pass
        return False
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def get_playwright_browsers_path(self):
        """Get the correct path to playwright browsers directory"""
        # Check if running as executable
        if getattr(sys, 'frozen', False):
            # Running as executable
            executable_dir = Path(sys.executable).parent
            browsers_path = executable_dir / ".playwright-browsers"
        else:
            # Running as script
            script_dir = Path(__file__).parent
            browsers_path = script_dir / ".playwright-browsers"
        
        return str(browsers_path.resolve())
        
    def start_automation(self):
        """Start the automation in a separate thread"""
        if self.is_running:
            return
            
        url = self.url_var.get().strip()
        time_str = self.time_var.get().strip()
        
        if not url:
            messagebox.showerror("エラー", "有効なURLを入力してください")
            return
            
        if not self.validate_time_format(time_str):
            messagebox.showerror("エラー", "有効な時間をHH:MM:SS.mmm形式で入力してください (例: 12:00:00.000 または 12:00)")
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="自動化実行中...")
        self.progress_var.set("ブラウザを起動中...")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        self.log_message("自動化を開始します...")
        self.log_message(f"目標時間: {time_str}")
        
        # Run automation in separate thread
        self.automation_thread = threading.Thread(target=self.run_automation_async, args=(url, time_str))
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def stop_automation(self):
        """Stop the automation"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="自動化を停止中...")
        self.progress_var.set("停止中...")
        self.log_message("自動化を停止中...")
        
    async def run_at_Date(self, page, target_time_str):
        """Modified run_at_Date function with GUI logging and custom time"""
        has_run_today = False
        
        # Parse target time with milliseconds support
        if '.' in target_time_str:
            # New format: HH:MM:SS.mmm
            time_part, millisecond_part = target_time_str.split('.')
            hour, minute, second = map(int, time_part.split(':'))
            millisecond = int(millisecond_part) if millisecond_part else 0
        else:
            # Old format: HH:MM
            hour, minute = map(int, target_time_str.split(':'))
            second = 0
            millisecond = 0
        
        self.log_message(f"{target_time_str}まで待機中...")

        while self.is_running:
            now = datetime.now()
            if (now.hour == hour and now.minute == minute and 
                now.second == second and now.microsecond // 1000 >= millisecond and 
                not has_run_today):
                self.log_message(f"🟢 {now.strftime('%H:%M:%S.%f')[:-3]}になりました! 関数を実行します...")
                self.progress_var.set(f"{now.strftime('%H:%M:%S.%f')[:-3]}になりました! 関数を実行します...")
                
                try:
                    await page.wait_for_selector("div.bt-area span#enter-bt-zumi a", timeout=None)
                    await page.click("div.bt-area span#enter-bt-zumi a")
                    self.log_message('div.bt-area span#enter-bt-zumi aをクリックしました')
                    
                    await page.wait_for_selector('div.accept-con input#i14', timeout=None)
                    await page.click('div.accept-con input#i14')
                    self.log_message('div.accept-con input#i14をクリックしました')
                    
                    await page.wait_for_selector('div.con input#i8', timeout=None)
                    await page.click('div.con input#i8')
                    self.log_message('div.con input#i8をクリックしました')
                    
                    await page.wait_for_selector('div.cont-block span.enter-bt span a', timeout=None)
                    await page.click('div.cont-block span.enter-bt span a')
                    self.log_message(f"✅ 完了")
                    has_run_today = True
                    return False
                except Exception as e:
                    self.log_message(f"❌ 実行中にエラーが発生しました: {str(e)}")
                    return False
                    
            if not self.is_running:
                break
                
            # Reset flag after target time has passed
            if (now.hour > hour or 
                (now.hour == hour and now.minute > minute) or
                (now.hour == hour and now.minute == minute and now.second > second) or
                (now.hour == hour and now.minute == minute and now.second == second and 
                 now.microsecond // 1000 > millisecond)):
                has_run_today = False
                
            await asyncio.sleep(0.001)  # Check every millisecond for precise timing

    async def run_automation(self, url, target_time_str):
        """Main automation function"""
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        
        # Set PLAYWRIGHT_BROWSERS_PATH to the correct location
        browsers_path = self.get_playwright_browsers_path()
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
        self.log_message(f"Playwright browsers path: {browsers_path}")
        
        try:
            async with async_playwright() as p:
                self.log_message("ブラウザを起動中...")
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(user_agent=user_agent)
                page = await context.new_page()

                # Avoid automation detection
                await page.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")

                self.log_message("URLに移動中...")
                self.progress_var.set("ページを読み込んでいます...")
                await page.goto(url, wait_until="load", timeout=300000)
                self.log_message("ページの読み込みが完了しました")
                self.progress_var.set(f"{target_time_str}まで待機中...")
                
                await self.run_at_Date(page, target_time_str)
                
                if self.is_running:
                    self.log_message("スクレイピングが完了しました。ブラウザは開いたままになります。")
                    await asyncio.sleep(30)  # Keep browser open for 30 seconds
                    
        except Exception as e:
            self.log_message(f"❌ エラー: {str(e)}")
        finally:
            if self.is_running:
                self.root.after(0, self.automation_finished)
    
    def run_automation_async(self, url, target_time_str):
        """Run automation in asyncio event loop"""
        asyncio.run(self.run_automation(url, target_time_str))
    
    def automation_finished(self):
        """Called when automation finishes"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="自動化が完了しました")
        self.progress_var.set("完了")
        self.log_message("自動化が完了しました")

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

import os
import smtplib
import sqlite3
import ssl
import sys
import time
import winsound

from pathlib import Path

from datetime import date
from datetime import datetime

from email.message import EmailMessage

# Get the current date
today = date.today()

formatted_date = today.strftime("%Y-%m-%d")

file_name = formatted_date + ".txt"

print("file_name", file_name)

directory_path = "c:/skmrsummary" # Replace with the actual path


def my_function():

    alarm_list = ["3B8FA", "39BFR", "6W1RD", "9J2FI", "C5R", "E51WL", "EL2BG", "FR4AW", "HZ1DG", "PJ6Y", "PY0FB", "SO1WS", "TR8CA", "TZ4AM", "V51WW", "VP2MAA", "ZD7CTO", "ZS6OB"]
    
    grid_list  = ["CM93", "CN74", "CN75", "CN93", "DL89", "DM23", "DM27", "DM39", "DN01", "DN02", "DN03", "DN04", "DN10", "DN12", "DN21", "DN24", "DN32"]
    
    line_count = 0
    skip_count = 0
    tilde_count = 0
    plus_count = 0
    colon_count = 0
    cq_count = 0
    last_occurence_char = 0
    skipCallSet = {"N1AAA"}
    last_time = "00:00:00"
        
    print(file_name)
    
    try:
        with open(file_name, 'r') as file:
            for line in file:
                
                call = ""
                grid = ""
        
                line_count = line_count + 1
                new_line = " ".join(line.strip().split())
                
                #print("new line ",new_line)
                
                # values[0] receiver_nbr
                # values[1] line_time
                # values[2] freq
                # values[3] mode
                # #01  01:36:30     50,313  FT8       25  0.1 1620 ~  CQ W5THT EM50
                
                values = new_line.split()
                line_seperator = values[7]
                
                line_time   = values[1]
                #print("line time ",line_time)
		
                compare_time(line_time)
                # go to next line if time has already been processed.
                # if line time is less than last run time then continue to next line
                
                if line_time > last_time:
                    print("practice time check stop line_time last_time", line_time, last_time)
                    #last_time = line_time
                    
                # #02  14:38:15     50,313  FT8        1  0.3 2658 ~  CQ K2TY EM60
                
                match line_seperator:
                        case "+":
                            plus_count = plus_count + 1
                            continue
                        case ":":
                            colon_count = colon_count + 1
                            continue
                        case "~":
                            tilde_count = tilde_count + 1
                            pass
                        case _:  # Default case, like 'else'
                            print(f"Unknown line_seperator: {line_seperator}")
                            sys.exit()
           
                
                                
                first_half = new_line.split(line_seperator)[0] # 10/22/2025
                                
                line_freq   = first_half.split(" ")[2]
                line_mode   = first_half.split(" ")[3]
                line_report = first_half.split(" ")[4]
                
                
                last = new_line.split(line_seperator)[1]
                firstField = last.split(" ")[1] 
                
                call = last.split(" ")[2]
                
                # check value 3 for 73 and R- !!!
                try:
                    grid = last.split(" ")[3]
                except ValueError as e:
                    # Handle cases where the split doesn't result in the expected number of items
                    print(f"Error processing line '{line}': {e}. Expected Grid got {len(last.split(''))}.")
                except Exception as e:
                    # Catch any other unexpected errors
                    print(f"An unexpected error occurred with line '{last}': {e}")
                                
                # last field could be grid, 73 or report
                #01  03:04:15     50,313  FT8       14  0.9 1514 ~  CQ KO5S EM50
                #04  13:51:30     50,275  Q65-30A   -9  0.2 1317 :  K0TPP AE5VB 73                        q0
                #04  13:42:00     50,275  Q65-30A    2  0.2 1657 :  KA2UQW AE5VB EM50                     q0
                #04  13:46:30     50,275  Q65-30A   -1  0.1 1657 :  K0TPP AE5VB R-10                      q0
                
                if firstField == "CQ":
                    cq_count = cq_count + 1
                    if call == "DX" or call == "DE" or call == "SW":       
                        grid = last.split(" ")[4]
                        call = last.split(" ")[3]
                    else:
                        # this fails when a cq doesn't have a grid
                        try:
                            grid = last.split(" ")[3]
                        except ValueError as e:
                            # Handle cases where the split doesn't result in the expected number of items
                            print(f"Error processing line '{line}': {e}. Expected Grid got {len(last.split(''))}.")
                        except Exception as e:
                            # Catch any other unexpected errors
                            print(f"An unexpected error occurred with line '{last}': {e}")
                
                # put call in list if cq but need to check skiplist for none cq lines
                if grid == "EM50" or grid == "EM60" or grid == "EL49":
                    skip_count = skip_count + 1
                    
                    if call in skipCallSet:
                        pass
                    else:
                        print("Adding Call to Skip List ",line_count, call, grid)
                        skipCallSet.add(call)
                    continue
                else:
                    
                    # if a station is not cq'ing they won't have a grid so this check is to skip those records
                    if call in skipCallSet:
                        skip_count = skip_count + 1
                        print(f"Not a CQ secondary check '{call}' is in the set.")
                        continue
                    else:
                        pass
                        #print(f"Second Check No, '{call}' is not in the set.")
                
                    conn = sqlite3.connect('my_database.db')
                    cursor = conn.cursor()
                    
                    # Insert data
                    cursor.execute("INSERT INTO sdralerts (sdr_call, sdr_grid, sdr_time, sdr_freq, sdr_mode, sdr_report) VALUES (?, ?, ?, ?, ?, ?)", (call, grid, line_time, line_freq, line_mode, line_report))
		            
                    conn.commit()
                
                if line_count % 10 == 0:
                    print("skip call check ", skipCallSet)
             
                if call in alarm_list:
                    print("Alarm Triggered ",call)
                    time.sleep(30)
                    send_text()
                    #send_email()
                    #sound_alarm()
                    
                if grid in grid_list:
                    print("Alarm Triggered ",call)
                    time.sleep(30)
                    send_text()
                    #send_email()
                    #sound_alarm()
                    
            print(" ")
            print("Line Count ", line_count)
        
            print(" ")
            print("Skip Count ", skip_count)
            
            print(" ")
            print("Tilde Count ", tilde_count)
            print("Plus Count ", plus_count)
            print("Colon Count ", colon_count)
            
            print("CQ Count ", cq_count)
            
            print("skip calls ", skipCallSet)
            
    except FileNotFoundError:
        current_time = get_time()
        print(f"Error: The file '{file_name}' was not found.", current_time)
    except Exception as e:
        print(f"An error occurred: {e}")
      

def compare_time(line_time):

    current_time = get_time()
    
    time_str1 = current_time   # "14:30:00" 

    time_str2 = line_time  # "09:15:00"

    format_string = "%H:%M:%S"

    dt_obj1 = datetime.strptime(time_str1, format_string).time()

    dt_obj2 = datetime.strptime(time_str2, format_string).time() 

    #print("date objects ",dt_obj1 > dt_obj2) # Output: True
    
    # this test works 10/21/2025
    #if dt_obj1 > dt_obj2:
    #    print("current time greater ", dt_obj1, dt_obj2)
    #else:
    #    print("line time greater ", dt_obj1, dt_obj2)
                
    

def sqlite_db():
    
    # #02  14:38:15     50,313  FT8        1  0.3 2658 ~  CQ K2TY EM60
    
    try:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
    
        # Create a table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sdralerts (
                id INTEGER PRIMARY KEY,
                sdr_call TEXT NOT NULL,
                sdr_grid TEST,
                sdr_time TEXT NOT NULL,
                sdr_freq REAL,
                sdr_mode TEXT NOT NULL,
                sdr_report TEST
            )
        ''')
       
        # Query data
        #cursor.execute("SELECT * FROM products WHERE price > ?", (1000,))
        #high_priced_products = cursor.fetchall()
        #print("Today's Alerts:")
        #for product in high_priced_products:
        #    print(product)
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    
    finally:
        if conn:
            conn.close()
        
        
def send_email():
    
    msg = EmailMessage()
    msg.set_content("This is the body of the email.")
    msg['Subject'] = 'SDR Alert for' 
    msg['From'] = 'gmacie@gmail.com'  # Replace with your email
    msg['To'] = 'gmacie@yahoo.com' # Replace with recipient's email

    # For Gmail, use 'smtp.gmail.com' and port 587 for TLS or 465 for SSL
    smtp_server = 'smtp.gmail.com'
    port = 587 # or 465 for SSL
    
    # Create a secure SSL context if using SSL
    # context = ssl.create_default_context() # If using SSL on port 465
    
    try:
        # Connect to the SMTP server (using TLS for port 587)
        server = smtplib.SMTP(smtp_server, port)
        server.starttls() # Enable TLS encryption
        server.login('gmacie@gmail.com', 'gvcd smvt ifal euvl') # Use your email and app password
        server.send_message(msg)
        print("Email sent successfully!")
    
    except Exception as e:
        print(f"Error sending email: {e}")
    
    finally:
        server.quit() # Close the connection
    
 
def send_text():
    # Your email account info (use an App Password for Gmail)
    sender_email = "gmacie@gmail.com"
    password = "gvcd smvt ifal euvl "
    
    # Recipient's phone number and carrier gateway address
    recipient_number = "4048197903"
    carrier_gateway = "vtext.com"  # visible (verizen)
    
    sms_gateway = f"{recipient_number}@{carrier_gateway}"
    
    # The message to send
    message = "YJ0RS 6 Meter Alert Test sent from Python."
    
    # Establish a secure connection and send the text
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, sms_gateway, message)
        print("Text sent successfully via email gateway!")
    except Exception as e:
        print(f"Error: {e}")

def get_time():
        
    # Get the current full datetime object
    current_datetime = datetime.now()
    
    # Extract only the time
    current_time_object = current_datetime.time()
    
    # Format the time as a string
    current_time = current_datetime.strftime("%H:%M:%S")
    
    #print(f"Current full datetime: {current_datetime}")
    
    #print(f"Current time object: {current_time_object}")
    #print(f"current time: {current_time}")

    return current_time
    
def sound_alarm():

    alarm_count = 0
    # Change the path and filename below
    sound = r"C:\Windows\Media\Alarm01.wav"

    interval = 1  # Change the interval in minutes here
    start_time = time.time()
    
    while True:
        alarm_count = alarm_count + 1  
        elapsed_time = int((time.time() - start_time) / 60)  # Elapsed time in minutes
        
        if elapsed_time % interval == 0:
            winsound.PlaySound(sound, winsound.SND_FILENAME)
            time.sleep(5)  # Change seconds here
            winsound.PlaySound(None, winsound.SND_PURGE)
        
        time.sleep(60)

def main():
    while True:

        
        my_function()
        time.sleep(60) # Wait for 60 seconds (1 minute)        

if __name__ == "__main__":
    
    get_time()
    
    print("Script name:", sys.argv[0])
    if len(sys.argv) > 1:
        print("First argument:", sys.argv[1])
    else:
        print("No arguments provided.")
    
    sqlite_db()
    main()
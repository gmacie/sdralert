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

    alarm_list = ["3B8FA", "39BFR", "9J2FI", "E51WL", "FR4AW", "PJ6Y", "PY0FB", "V51WW", "TZ4AM", "VP2MAA", "ZD7CTO", "ZS6OB"]
    grid_list  = ["CM93", "CN74", "CN75", "CN93", "DL89", "DM23", "DM27", "DM39", "EM43"]
    
    lineCount = 0
    skipCount = 0
    tildeCount = 0
    plusCount = 0
    colonCount = 0
    last_occurence_char = 0
    skipCallSet = {"N1AAA"}
    lastTime = "00:00:00"
        
    print(file_name)
    
    try:
        with open(file_name, 'r') as file:
            for line in file:
                
                call = ""
                grid = ""
                
                #print(line.strip())  # .strip() removes leading/trailing whitespace, including the newline character
        
                lineCount = lineCount + 1
                new_line = " ".join(line.strip().split())
                
                #print("new line ",new_line)
                
                values = new_line.split()
                line_seperator = values[7]
                #print("line seperator ", line_seperator)
                
                line_time   = values[1]
                #print("line time ",line_time)
		
                compare_time(line_time)
                
                #sys.exit()
                # #02  14:38:15     50,313  FT8        1  0.3 2658 ~  CQ K2TY EM60
                
                match line_seperator:
                        case "+":
                            plusCount = plusCount + 1
                            continue
                        case ":":
                            colonCount = colonCount + 1
                            continue
                        case "~":
                            tildeCount = tildeCount + 1
                            pass
                        case _:  # Default case, like 'else'
                            print(f"Unknown line_seperator: {line_seperator}")
                            sys.exit()
               
                #if lineCount == 10:
                #    sys.exit()
                    
                #last = new_line.split("~")[1] 
                
                last = new_line.split(line_seperator)[1] 
                                
                #first_half  = new_line.split("~")[0]
                first_half = new_line.split(line_seperator)[0] # 10/22/2025
                                
                line_freq   = first_half.split(" ")[2]
                line_mode   = first_half.split(" ")[3]
                line_report = first_half.split(" ")[4]
                
                firstField = last.split(" ")[1]
                call = last.split(" ")[2]
                                
                # last field could be grid, 73 or report
                if firstField == "CQ":
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
                    skipCount = skipCount + 1
                    print("Adding Grid ",lineCount, grid, call)
                    skipCallSet.add(call)
                    continue
                else:
                    print("Good Line ",lineCount, new_line)
                    
                    conn = sqlite3.connect('my_database.db')
                    cursor = conn.cursor()
                    
                    # Insert data
                    cursor.execute("INSERT INTO sdralerts (sdr_call, sdr_grid, sdr_time, sdr_freq, sdr_mode, sdr_report) VALUES (?, ?, ?, ?, ?, ?)", (call, grid, line_time, line_freq, line_mode, line_report))
		            
                    conn.commit()
                
                # if a station is not cq'ing they won't have a grid so this check is to skip those records
                value_to_check = call
                if value_to_check in skipCallSet:
                    skipCount = skipCount + 1
                    print(f"Yes, '{value_to_check}' is in the set.")
                    continue
                else:
                    print(f"No, '{value_to_check}' is not in the set.")
                
                if lineCount % 10 == 0:
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
            print("Line Count ", lineCount)
        
            print(" ")
            print("Skip Count ", skipCount)
            
            print(" ")
            print("Break Count ", tildeCount)
            print("Plus Count ", plusCount)
            print("Colon Count ", colonCount)
            
            print("skip calls ", skipCallSet)
            
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
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

while True:

    get_time()
    
    print("Script name:", sys.argv[0])
    if len(sys.argv) > 1:
        print("First argument:", sys.argv[1])
    else:
        print("No arguments provided.")
    
    sqlite_db()
    my_function()
    time.sleep(60) # Wait for 60 seconds (1 minute)           
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

import tempfile

with tempfile.TemporaryDirectory() as td:
    f_name = os.path.join(td, 'test')
    with open(f_name, 'w') as fh:
        fh.write('<content>')
    # Now the file is written and closed and can be used for reading.


# Get the current date
today = date.today()

formatted_date = today.strftime("%Y-%m-%d")

file_name = formatted_date + ".txt"

print("file_name", file_name)

current_directory_path = Path.cwd()
print(f"Current working directory (Path.cwd()): {current_directory_path}")

def my_function():

    alarm_list = ["3B8FA", "39BFR", "5Z4VJ", "6W1RD", "9J2FI", "C5R", 
                  "E51WL", "EL2BG", "FR4OO", "FR4AW", "HZ1DG", "PY0FB", "SO1WS", "TR8CA", "TY5AD", "TZ4AM", "V51WW", "VP2MAA", "ZD7CTO", "ZS6OB"]
    
    # 445 CONF NEED 43
    grid_list  = ["CM93",
                  "CN74", "CN75", "CN93",
                  "DL89",
                  "DM23", "DM27", "DM39", "DM46", "DM49", "DM56",
                  "DN01", "DN02", "DN03", "DN04", "DN08", "DN10", "DN12", "DN21", "DN24", "DN32", "DN38", "DN42", "DN44", "DN48", "DN51", "DN52", "DN54", "DN58",
                  "DN64", "DN67", "DN68", "DN75", "DN76", "DN78", "DN98",
                  "EL07", "EL39",
                  "EM07", "EM23",
                  "FN56", "FN57", "FN66"]
    
    line_count = 0
    skip_count = 0
    time_skip_count = 0
    tilde_count = 0
    plus_count = 0
    colon_count = 0
    cq_count = 0
    last_occurence_char = 0
    skipCallSet = {"N1AAA"}
    
    os.system('cls')
    
    formatted_date = today.strftime("%Y-%m-%d")

    file_name = formatted_date + ".txt"  

    print("file_name", file_name)
    print(" ")
          
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
                		
                compare_time(line_time)
                # go to next line if time has already been processed.
                # if line time is less than last run time then continue to next line
                
                if line_time > last_time:
                    pass
                    #print("practice time check stop line_time last_time", line_time, last_time)
                    #last_time = line_time
                else:
                    time_skip_count = time_skip_count + 1
                    continue
                    
                # #02  14:38:15     50,313  FT8        1  0.3 2658 ~  CQ K2TY EM60
                
                match line_seperator:
                        case "+":
                            plus_count = plus_count + 1
                            continue
                        case ":":
                            # Q65-30A
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
                print("First field ", line_count, last, firstField)
                input
                
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
                #ok 01  03:04:15     50,313  FT8       14  0.9 1514 ~  CQ KO5S EM50
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
                            #print(f"An unexpected error occurred with line looking for grid'{last}': {e}")
                            print("No Grid on CQ")
                
                match grid:
                        case "RR73" | "73" | "RRR":
                            grid = ""
                        case "~":
                            pass
                        case _:  # Default case, like 'else'
                            pass
                
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
                    print("Line ", line_count, new_line)
                    
                    cursor.execute("INSERT INTO sdralerts (sdr_call, sdr_grid, sdr_time, sdr_freq, sdr_mode, sdr_report, sdr_fname) VALUES (?, ?, ?, ?, ?, ?, ?)", (call, grid, line_time, line_freq, line_mode, line_report, file_name))
		            
                    conn.commit()
                           
                if call in alarm_list:
                    print("Alarm Triggered ",call)
                    #time.sleep(30)
                    message = f"{call} 6 Meter Alert Test sent from Python. {line_freq}"
                    send_text(message)
                    print("Sent text ")
                    #send_email()
                    #print("Sent email ")
                    #sound_alarm()
                    
                if grid in grid_list:
                    print("Alarm Triggered ",call)
                    time.sleep(30)
                    send_text()
                    #send_email()
                    #sound_alarm()
                    
            print(" ")
            print("Time Skip ", time_skip_count)
            
            print(" ")
            print("Tilde Count ", tilde_count)
            print("Plus Count ", plus_count)
            print("Colon Count ", colon_count)
                    
            print(" ")
            print("Line Count ", line_count)
        
            print(" ")
            print("Skip Count ", skip_count)
                      
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
                sdr_report TEXT,
                sdr_fname TEXT
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
    msg['To'] = 'gmacie@yahoo.com' #, 'gmacie@gmail.com' # Replace with recipient's email

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
    
 
def send_text(text_msg):
    # Your email account info (use an App Password for Gmail)
    sender_email = "gmacie@gmail.com"
    password = "gvcd smvt ifal euvl "
    
    # Recipient's phone number and carrier gateway address
    recipient_number = "4048197903"
    carrier_gateway = "vtext.com"  # visible (verizen)
    
    sms_gateway = f"{recipient_number}@{carrier_gateway}"
    
    # The message to send
    #message = f"{text_call} 6 Meter Alert Test sent from Python. {line_freq}"
    message = text_msg
    
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
        pass
        #print("No arguments provided.")
        
    file_path = "last_time.txt"
    
    last_time = "00:00:00" # default to midnight
    # need to delete the file at 23:59 every night
    
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline()
            print(f"The first line is: {first_line.strip()}") # .strip() removes trailing newline characters
            last_time = first_line
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    print("Last Time ", last_time)
    
    sqlite_db()
    main()
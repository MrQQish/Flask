### when file is uploaded read the IDX to generate event info
# events can then be selected or expanded on by pre-reading the event bin 
# events are assigned MD5 hashes as they are raed/stored into UI 
import struct

def read_idx(idx_filename: str):
    with open(idx_filename, 'rb') as idx_file:
        idx = idx_file.read()

        # check for reading error
        if idx == None:
            print(f"Error: Failed to read IDX file \"{idx_filename}\".")
            exit()

        # unpack
        event_struct = struct.iter_unpack("=iqqq", idx)
        event_indexes = [i for i in event_struct] # produce a list of tuples

        return event_indexes

def read_event():
    
    return


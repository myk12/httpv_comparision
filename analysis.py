import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

class HTTP_COMP:
    def __init__(self) -> None:
        self.http1_datapath = ''
        self.http2_datapath = ''
        self.http3_datapath = ''
        self.http1 = {}
        self.http2 = {}
        self.http3 = {}

    def load_data(self, dir):
        subdirs = os.listdir(dir)
        for subdir in subdirs:
            if subdir == 'http1.1':
                self.http1_datapath = dir + '/' + subdir
                self.load_data_from_path(self.http1_datapath, 'http1.1')
            elif subdir == 'http2':
                self.http2_datapath = dir + '/' + subdir
                self.load_data_from_path(self.http2_datapath, 'http2')
            elif subdir == 'http3':
                self.http3_datapath = dir + '/' + subdir
                self.load_data_from_path(self.http3_datapath, 'http3')

    def load_data_from_path(self, path, protocol):
        files = os.listdir(path)
        for file in files:
            # file format: delay_%d_loss_%d.csv
            with open(path + '/' + file, 'r') as f:
                df = pd.read_csv(f)
                # extract delay and loss
                delay = file.split('_')[1]
                loss = file.split('_')[3].split('.')[0]

                if protocol == 'http1.1':
                    self.http1[(delay, loss)] = df
                elif protocol == 'http2':
                    self.http2[(delay, loss)] = df
                elif protocol == 'http3':
                    self.http3[(delay, loss)] = df
    
    def plot_delay_comparision(self):
        # plot http1.1 http2 http3 delay comparision
        delay_array = [0, 50, 100, 150, 200, 250, 300]
        loss_array = [0, 5, 10, 15, 20]

        # plot five subplots of loss = 0, 5, 10, 15, 20
        # every subplot contains http1.1 http2 http3 comparision
        fig, axs = plt.subplots(1, 5, figsize=(20, 5))

        for i in range(len(loss_array)):
            loss = loss_array[i]
            http1_delay = []
            http2_delay = []
            http3_delay = []
            for j in range(len(delay_array)):
                delay = delay_array[j]
                http1_delay.append(self.http1[(str(delay), str(loss))]['time_total'].mean())
                http2_delay.append(self.http2[(str(delay), str(loss))]['time_total'].mean())
                http3_delay.append(self.http3[(str(delay), str(loss))]['time_total'].mean())
            axs[i].plot(delay_array, http1_delay, label='http1.1')
            axs[i].plot(delay_array, http2_delay, label='http2')
            axs[i].plot(delay_array, http3_delay, label='http3')
            axs[i].set_title('loss = ' + str(loss) + '%')
            axs[i].set_xlabel('delay (ms)')
            axs[i].set_ylabel('completion time (s)')
            axs[i].legend()
        
        plt.savefig('delay_comparision.png')

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='HTTP version comparision')
    parser.add_argument('--dir', type=str, default='data', help='Directory of data')

    args = parser.parse_args()

    http_comp = HTTP_COMP()
    http_comp.load_data(dir=args.dir)
    http_comp.plot_delay_comparision()
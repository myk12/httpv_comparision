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

        self.delay_array = []
        self.loss_array = []

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

                if delay not in self.delay_array:
                    self.delay_array.append(delay)
                if loss not in self.loss_array:
                    self.loss_array.append(loss)

                if protocol == 'http1.1':
                    self.http1[(delay, loss)] = df
                elif protocol == 'http2':
                    self.http2[(delay, loss)] = df
                elif protocol == 'http3':
                    self.http3[(delay, loss)] = df
    
    def plot_delay_comparision(self):
        # plot http1.1 http2 http3 delay comparision accrording to delay and loss array

        # plot subplots in a row, the number of subplots is the size of loss_array
        # every subplot contains http1.1 http2 http3 comparision
        fig, axs = plt.subplots(1, len(self.loss_array), figsize=(5*len(self.loss_array), 5))

        for i in range(len(self.loss_array)):
            loss = self.loss_array[i]
            http1_delay = []
            http2_delay = []
            http3_delay = []

            for j in range(len(self.delay_array)):
                delay = self.delay_array[j]
                http1_delay.append(self.http1[(delay, loss)]['time_total'].mean())
                http2_delay.append(self.http2[(delay, loss)]['time_total'].mean())
                http3_delay.append(self.http3[(delay, loss)]['time_total'].mean())
            
            axs[i].plot(self.delay_array, http1_delay, label='http1.1')
            axs[i].plot(self.delay_array, http2_delay, label='http2')
            axs[i].plot(self.delay_array, http3_delay, label='http3')
            axs[i].set_title('loss = ' + str(loss) + '%')
            axs[i].set_xlabel('delay (ms)')
            axs[i].set_ylabel('completion time (s)')
            axs[i].legend()

        plt.savefig('delay_comparision.png')
    
    def plot_loss_comparision(self):
        # plot http1.1 http2 http3 loss comparision accrording to delay and loss array

        # plot subplots in a row, the number of subplots is the size of delay_array
        # every subplot contains http1.1 http2 http3 comparision
        fig, axs = plt.subplots(1, len(self.delay_array), figsize=(5*len(self.delay_array), 5))

        for i in range(len(self.delay_array)):
            delay = self.delay_array[i]
            http1_loss = []
            http2_loss = []
            http3_loss = []

            for j in range(len(self.loss_array)):
                loss = self.loss_array[j]
                http1_loss.append(self.http1[(delay, loss)]['time_total'].mean())
                http2_loss.append(self.http2[(delay, loss)]['time_total'].mean())
                http3_loss.append(self.http3[(delay, loss)]['time_total'].mean())
            
            axs[i].plot(self.loss_array, http1_loss, label='http1.1')
            axs[i].plot(self.loss_array, http2_loss, label='http2')
            axs[i].plot(self.loss_array, http3_loss, label='http3')
            axs[i].set_title('delay = ' + str(delay) + 'ms')
            axs[i].set_xlabel('loss (%)')
            axs[i].set_ylabel('completion time (s)')
            axs[i].legend()

        plt.savefig('loss_comparision.png')

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='HTTP version comparision')
    parser.add_argument('--dir', type=str, default='data', help='Directory of data')

    args = parser.parse_args()

    http_comp = HTTP_COMP()
    http_comp.load_data(dir=args.dir)
    http_comp.plot_delay_comparision()
    http_comp.plot_loss_comparision()
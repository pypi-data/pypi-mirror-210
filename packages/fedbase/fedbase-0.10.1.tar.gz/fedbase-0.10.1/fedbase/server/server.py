# from nodes.node import node
import torch
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pandas.plotting import parallel_coordinates
import traceback

class server_class():
    def __init__(self, device):
        self.device = device
        self.test_metrics = []
        self.clustering = {'label':[], 'raw':[], 'center':[]}

    def assign_model(self, model):
        try:
            self.model.load_state_dict(model.state_dict())
        except:
            self.model = model
        self.model.to(self.device)

    def aggregate(self, node_id_list, model_list, weight_list):
        aggregated_weights = self.model.state_dict()
        for j in aggregated_weights.keys():
            aggregated_weights[j] = torch.zeros(aggregated_weights[j].shape).to(self.device)
        weight_list = [i/sum(weight_list) for i in weight_list]
        for i in node_id_list:
            for j in model_list[i].state_dict().keys():
                aggregated_weights[j] += model_list[i].state_dict()[j]*weight_list[i]
        return aggregated_weights

    def aggregate(self, model_list, weight_list):
        aggregated_weights = model_list[0].state_dict()
        for j in aggregated_weights.keys():
            aggregated_weights[j] = torch.zeros(aggregated_weights[j].shape).to(self.device)
        # sum_size = sum([nodes[i].data_size for i in idlist])
        for i in range(len(model_list)):
            for j in model_list[i].state_dict().keys():
                aggregated_weights[j] += model_list[i].state_dict()[j]*weight_list[i]
        return aggregated_weights
    
    def distribute(self, model_in_list, model_dis_dict = None):
        if not model_dis_dict:
            model_dis_dict = self.model.state_dict()
        for i in model_in_list:
            i.load_state_dict(model_dis_dict)

    def acc(self, nodes, weight_list):
        global_test_metrics = [0]*2
        for i in range(len(weight_list)):
            for j in range(len(global_test_metrics)):
                global_test_metrics[j] += weight_list[i]*nodes[i].test_metrics[-1][j]
        print('GLOBAL Accuracy, Macro F1 is %.2f %%, %.2f %%' % (100*global_test_metrics[0], 100*global_test_metrics[1]))
        self.test_metrics.append(global_test_metrics)

    def client_sampling(self, frac, distribution):
        pass

    def test(self, test_loader):
        correct = 0
        total = 0
        with torch.no_grad():
            for data in test_loader:
                inputs, labels = data
                inputs = inputs.to(self.device)
                labels = torch.flatten(labels)
                labels = labels.to(self.device, dtype = torch.long)
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        print('Accuracy on the %d test cases: %.2f %%' % (total, 100*correct / total))
        # torch.cuda.empty_cache()

    def model_similarity(model_repr_1, model_repr_2, repr='output'):
        if repr == 'output':
            self.similarity = (log(model_repr_1)-log(model_repr_2)).sum(axis=1).abs()

    def weighted_clustering(self, nodes, idlist, K, weight_type='data_size'):
        weight = []
        X = []
        sum_size = sum([nodes[i].data_size for i in idlist])
        # print(list(nodes[0].model.state_dict().keys()))
        for i in idlist:
            if weight_type == 'equal':
                weight.append(1/len(idlist))
            elif weight_type == 'data_size':
                weight.append(nodes[i].data_size/sum_size)
            X.append(np.array(torch.flatten(nodes[i].model.state_dict()[list(nodes[i].model.state_dict().keys())[-2]]).cpu()))
        # print(X, np.array(X).shape)
        kmeans = KMeans(n_clusters=K, n_init = 5).fit(np.asarray(X), sample_weight= weight)
        labels = kmeans.labels_
        print(labels)
        print([list(labels).count(i) for i in range(K)])
        for i in idlist:
            nodes[i].label = labels[i]
        self.clustering['label'].append(list(labels.astype(int)))
        # self.clustering['raw'].append(X)
        # self.clustering['center'].append(kmeans.cluster_centers_)

    def calculate_B(self, nodes, idlist):
        sum_size = sum([nodes[i].data_size for i in idlist])
        # print(idlist, sum_size)
        avg = sum([sum(nodes[i].grads)*(nodes[i].data_size)/sum_size for i in idlist])
        # print(avg[-10:], nodes[idlist[0]].grads[0][-10:])
        # print(avg.shape, nodes[idlist[0]].grads.shape)
        B_list = []
        u_list = []
        for i in idlist:
            # print(torch.norm((sum(nodes[i].grads) - avg), 1)/torch.norm(avg, 1))
            # print(torch.norm((sum(nodes[i].grads) - avg), 1))
            u_list.append(float(torch.norm((sum(nodes[i].grads) - avg), 2)))
            B_list.append(float(torch.norm((sum(nodes[i].grads) - avg), 2)/torch.norm(avg, 2)))
            # nodes[i].grads = []
            # print(torch.norm(nodes[i].grads - avg, 2),torch.norm(avg, 2))
        return B_list, u_list

    def clustering_plot(self):
        # print(self.clustering)
        # self.clustering =[[1,1,2,2,3,3],[1,1,1,2,2,2],[1, 1, 1, 2, 2, 2],[1, 1, 1, 2, 2, 2]]
        col = [str(i) for i in range(len(self.clustering))]+['id']
        self.clustering.append(list(range(len(self.clustering[0]))))
        data= pd.DataFrame(np.array(self.clustering).T,columns= col)
        for i in data.columns:
            data[i]=data[i].apply(lambda x: str(x))
        # Make the plot
        parallel_coordinates(data, 'id', colormap=plt.get_cmap("Set2"))
        plt.show()

from fedbase.utils.data_loader import data_process, log
from fedbase.nodes.node import node
from fedbase.utils.tools import add_
from fedbase.server.server import server_class
from fedbase.baselines import fedavg
import torch
from torch.utils.data import DataLoader
import torch.optim as optim
from fedbase.model.model import CNNCifar, CNNMnist
import os
import sys
import inspect
from functools import partial

def run(dataset_splited, batch_size, K, num_nodes, model, objective, optimizer, warmup_rounds, global_rounds, local_steps, \
    reg = None, device = torch.device('cuda' if torch.cuda.is_available() else 'cpu'), finetune=False, finetune_steps = None):
    train_splited, test_splited, split_para = dataset_splited
    # warm up
    model_g = fedavg.run(dataset_splited, batch_size, num_nodes, model, objective, optimizer, warmup_rounds, local_steps, device, log_file = False)

    # initialize
    server = server_class(device)
    server.assign_model(model_g)

    nodes = [node(i, device) for i in range(num_nodes)]

    for i in range(num_nodes):
        # data
        # print(len(train_splited[i]), len(test_splited[i]))
        nodes[i].assign_train(DataLoader(train_splited[i], batch_size=batch_size, shuffle=True))
        nodes[i].assign_test(DataLoader(test_splited[i], batch_size=batch_size, shuffle=False))
        # objective
        nodes[i].assign_objective(objective())
        nodes[i].assign_model(model())
        nodes[i].model_g = model().to(device)
        nodes[i].assign_optim({'local_0': optimizer(nodes[i].model.parameters()),\
                'local_1': optimizer(nodes[i].model_g.parameters()),\
                    'all': optimizer(list(nodes[i].model.parameters())+list(nodes[i].model_g.parameters()))})

    del train_splited, test_splited

    # initialize K cluster model
    cluster_models = [model().to(device) for i in range(K)]

    weight_list = [nodes[i].data_size/sum([nodes[i].data_size for i in range(num_nodes)]) for i in range(num_nodes)]
    
    # distribute global model to model_g
    server.distribute([nodes[i].model_g for i in range(num_nodes)])

    # train!
    for i in range(global_rounds - warmup_rounds):
        print('-------------------Global round %d start-------------------' % (i))

        # local update model_0 for cluster model
        for j in range(num_nodes):
            nodes[j].local_update_steps(local_steps, partial(nodes[j].train_single_step_res, optimizer = nodes[j].optim['local_0'], \
                model_opt = nodes[j].model, model_fix = nodes[j].model_g)) 

        # server clustering
        assignment = [[] for _ in range(K)]
        for i in range(num_nodes):
            m = 0
            for k in range(1, K):
                # if i <=5:
                #     print(nodes[i].local_train_acc(cluster_models[m]), nodes[i].local_train_acc(cluster_models[k]))
                # if nodes[i].local_train_loss(cluster_models[m])>=nodes[i].local_train_loss(cluster_models[k]):
                if nodes[i].local_train_acc(cluster_models[m])<=nodes[i].local_train_acc(cluster_models[k]):
                    m = k
            assignment[m].append(i)
            nodes[i].label = m

        server.clustering['label'].append(assignment) 
        # print(assignment)
        print([len(assignment[i]) for i in range(len(assignment))]) 

        # server aggregation and distribution by cluster
        for k in range(K):
            if len(assignment[k])>0:
                model_k = server.aggregate([nodes[i].model for i in assignment[k]], \
                    [nodes[i].data_size/sum([nodes[i].data_size for i in assignment[k]]) for i in assignment[k]])
                server.distribute([nodes[i].model for i in assignment[k]], model_k)
                cluster_models[k].load_state_dict(model_k)

        # local update model_g for global model
        for j in range(num_nodes):
            nodes[j].local_update_steps(local_steps, partial(nodes[j].train_single_step_res, optimizer = nodes[j].optim['local_1'],\
                model_opt = nodes[j].model_g, model_fix = nodes[j].model))
            
        # aggregate model_g
        server.model.load_state_dict(server.aggregate([nodes[i].model_g for i in range(num_nodes)], weight_list))
        # distribute global model to model_g
        server.distribute([nodes[i].model_g for i in range(num_nodes)])
 
        # test accuracy
        for j in range(num_nodes):
             nodes[j].local_test(model_res = nodes[j].model_g)
        server.acc(nodes, weight_list)

    if not finetune:
        assign = [[i for i in range(num_nodes) if nodes[i].label == k] for k in range(K)]
        # log
        log(os.path.basename(__file__)[:-3] + add_(K) + add_(reg) + add_(split_para), nodes, server)
        return cluster_models, assign
    else:
        if not finetune_steps:
            finetune_steps = local_steps
        # fine tune
        # local update model for cluster model
        for j in range(num_nodes):
            nodes[j].local_update_steps(local_steps, partial(nodes[j].train_single_step_res, optimizer = nodes[j].optim['local_0'], \
                model_opt = nodes[j].model, model_fix = nodes[j].model_g)) 
        
        # local update model_g for global model
        for j in range(num_nodes):
            nodes[j].local_update_steps(local_steps, partial(nodes[j].train_single_step_res, optimizer = nodes[j].optim['local_1'],\
                model_opt = nodes[j].model_g, model_fix = nodes[j].model))
            nodes[j].local_test()
        server.acc(nodes, weight_list)
        # log
        log(os.path.basename(__file__)[:-3] + add_('finetune') + add_(K) + add_(reg) + add_(split_para), nodes, server)
        return [nodes[i].model for i in range(num_nodes)]
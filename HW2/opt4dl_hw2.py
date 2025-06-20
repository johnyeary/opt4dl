# -*- coding: utf-8 -*-
"""OPT4DL-HW2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LNOYNd87euoZExCCmhRJQOl-fa3LvRVl
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#sigma
def sigma(x):
  return np.maximum(x,0)

# derivative of sigma
def der_sigma(x):
  return np.where(x>0,1,0)

#loss fn
def L(y_true, y_pred):
    return np.mean(np.square(y_true-y_pred))

# gradient
def grad_L(y, w, x):
  pred = np.matmul(x,w)
  return np.array(-2*np.dot(x.T,((y-sigma(pred))*der_sigma(pred))))

# sample with replacement
def samp_with_rep(N,x,y):
  idx = np.random.randint(0,N)
  return x[idx,:],y[idx]

# sample without replacement
def samp_without_rep(N,x,y):
  idx = np.random.permutation(N)
  return (x[idx],y[idx])

# list out constants
d = 200
N = 1000
rng = np.random.default_rng()
e = rng.normal(0.0,0.05,size=(N,1))
w_init = rng.normal(0,1.5,size=(d,1))
w_act = rng.normal(0,1,size=(d,1))
x = rng.uniform(0,1,size=(N,d))
eta = 0.001 #learning rate
T = N #max epoch for sample w/out replace
q = 10 #q values for c and d
outlier_factor = 1.2  # Control the magnitude of outliers
outlier_indices = np.random.choice(N, size=int(0.01 * N), replace=False) #1% outliers
y = np.array(sigma(np.matmul(x,w_act)) + e)
y[outlier_indices] = outlier_factor * (y[outlier_indices])
errtol = 1e-6 #tolerance for stopping

def SGD(w,x,y,samp_idx,eta,errtol):
  x_jj = np.atleast_2d(x[samp_idx,:])
  y_jj = np.atleast_2d(y[samp_idx]).T

  w = w - eta*grad_L(y_jj,w,x_jj)
  loss = L(y,sigma(np.matmul(x,w)))
  return loss,np.abs(loss)<errtol,w

#parts a,b,c,d initialized
w_a = w_init
w_b = w_init
w_c = w_init
w_d = w_init
a_conv = False
printedA = False
b_conv = False
printedB = False
c_conv = False
printedC = False
d_conv = False
printedD = False
Loss_a = []
Loss_b = []
Loss_c = []
Loss_d = []
Loss_init = L(y,sigma(np.matmul(x,w_a)))
#initialize dataframes for sorting
df_c = pd.DataFrame(x,columns = [f'feature{ii}' for ii in range(d)])
df_c['target'] = y.flatten()
df_d = df_c.copy(deep = True) #deep copy
#initial losses
Loss_a.append(Loss_init)
Loss_b.append(Loss_init)
Loss_c.append(Loss_init)
Loss_d.append(Loss_init)

#part a, with replacement
samp_idx_a = np.random.choice(N,size=T,replace=True)
#part b, without replacement
samp_idx_b = np.random.choice(N,size=T,replace=False)
for ii in range(T):
  print(f'Epoch: {ii}')
  #check if each has converged; then check if I need to print anything
  # append the loss from this iteration to the Loss list for this epoch
  if not a_conv:
    loss_a,a_conv,w_a = SGD(w_a,x,y,samp_idx_a[ii],eta,errtol)
    Loss_a.append(loss_a)
    print(f"A Loss: {loss_a}")
  elif not printedA:
    print(f"A Converged after {ii} epochs")
    printedA = True
  #part b, apply sample w/out replacement
  if not b_conv:
    loss_b,b_conv,w_b = SGD(w_b,x,y,samp_idx_b[ii],eta,errtol)
    Loss_b.append(loss_b)
    print(f'B Loss: {loss_b}')
  elif not printedB:
    print(f"B Converged after {ii} epochs")
    printedB = True

  #part c, sorting by losses
  if not c_conv:
    df_c['pred'] = sigma(np.matmul(df_c.iloc[:,:d].values,w_c))
    df_c['loss'] = np.square(df_c['target']-df_c['pred']) #find loss for each sample
    max_loss_idx = df_c['loss'].nlargest(q).index #sort by loss
    loss_c,c_conv,w_c = SGD(w_c,df_c.iloc[:,:d].values,df_c['target'].values,max_loss_idx,eta,errtol)
    Loss_c.append(loss_c)
    print(f"C Loss: {loss_c}")
  elif not printedC:
    print(f"C Converged after {ii} epochs")
    printedC = True

  #part d, sorting by norm of sample gradients
  if not d_conv:
    df_d['grad_norm'] = df_d.apply(lambda row: np.linalg.norm(grad_L(np.atleast_2d(row['target']),w_d,np.atleast_2d(row.iloc[:d].values))),axis=1) #apply grad_L to each row
    max_grad_idx = df_d['grad_norm'].nlargest(q).index #sort by gradient norm
    loss_d,d_conv,w_d = SGD(w_d,df_d.iloc[:,:d].values,df_d['target'].values,max_grad_idx,eta,errtol)
    Loss_d.append(loss_d)
    print(f"D Loss: {loss_d}")
  elif not printedD:
    print(f"D Converged after {ii} epochs")
    printedD = True
#end T

epochs = np.arange(1,T+1)
plt.plot(epochs,Loss_a[1:],label='a')
plt.plot(epochs,Loss_b[1:],label='b')
plt.plot(epochs,Loss_c[1:],label='c')
plt.plot(epochs,Loss_d[1:],label='d')
plt.title(f'Loss vs. Epochs-Learning Rate ={eta}')
plt.xlabel('Epochs')
plt.ylabel('Loss-MSE')
plt.legend()
plt.show()
#plt.semilogx(epochs,Loss_a[1:],label='a')
#plt.semilogx(epochs,Loss_b[1:],label='b')
#plt.semilogx(epochs,Loss_c[1:],label='c')
#plt.semilogx(epochs,Loss_d[1:],label='d')
#plt.title(f'Loss vs. Epochs-Learning Rate ={eta}')
#plt.xlabel('Epochs (log scaled)')
#plt.ylabel('Loss-MSE')
#plt.legend()
#plt.show()

plt.loglog(epochs,Loss_a[1:],label='a')
plt.loglog(epochs,Loss_b[1:],label='b')
plt.loglog(epochs,Loss_c[1:],label='c')
plt.loglog(epochs,Loss_d[1:],label='d')
plt.title(f'Loss vs. Epochs-Learning Rate ={eta}')
plt.xlabel('log(Epochs)')
plt.ylabel('log(Loss-MSE)')
plt.legend()
plt.show()
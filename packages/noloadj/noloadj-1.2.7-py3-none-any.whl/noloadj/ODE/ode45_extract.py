import jax.numpy as np
from jax.lax import *
from jax import custom_jvp,jvp,interpreters
from functools import partial
from noloadj.ODE.ode45 import rk_step_der,interpolation,next_step_simulation

def odeint45_extract(f,x0,*P,T=0.,h0=1e-5,tol=1.48e-8):
    return _odeint45(f,h0,tol,x0,T,*P)


@partial(custom_jvp,nondiff_argnums=(0,1,2))
def _odeint45(f,h0,tol,x0,T,*P):
    type,cond_stop=f.stop

    def cond_fn(state):
        x_prev2,_,_,x_prev,t_prev,_,h,cstr,_,_=state
        if type=='seuil':
            val,seuil=cond_stop(x_prev,f.xnames)
            valp,_=cond_stop(x_prev2,f.xnames)
            return (h>0) & (np.sign(val-seuil)==np.sign(valp-seuil))
        else:
            return (h > 0) & cond_stop(t_prev,t_prev+h,cstr)


    def body_fn(state):
        _,_,_,x_prev,t_prev,y_prev,h,cstr,i,c=state

        x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                    i,c,h,f,tol,h0,T,*P)

        if type=='seuil':
            output,seuil=cond_stop(x,f.xnames)
            outputprev,_=cond_stop(x_prev,f.xnames)
            x,hopt,_,_,t_now,_,y,_,_=cond(
                np.sign(output-seuil)!=np.sign(outputprev-seuil),interpolation,
                lambda state:state,(x,hopt,x_prev,t_prev,t_now,y_prev,y,
                                    output-seuil,outputprev-seuil))
        elif isinstance(type,float):
            x=np.where(t_now>type,((x_prev-x)*type+t_prev*x-t_now*x_prev)
                       /(t_prev-t_now),x)
            y=np.where(t_now>type,((y_prev-y)*type+t_prev*y-t_now*y_prev)
                       /(t_prev-t_now),y)
            t_now,hopt=np.where(t_now>type,type,t_now),\
                       np.where(t_now>type,type-t_prev,hopt)

        if f.constraints!={}:
            for i in f.constraints.keys():
                if isinstance(f.constraints[i][1],tuple):
                    test_exp,(_,expression,_,_,_,_,name)=f.constraints[i]
                else:
                    (_,expression,_,_,_,_,name)=f.constraints[i]
                    test_exp = lambda t: True
                ind=f.xnames.index(name)
                cstr[i]=np.where(test_exp(t_now),expression(t_prev,x_prev[ind],
                            t_now,x[ind],cstr[i],h,T),cstr[i])

        return x_prev,t_prev,y_prev,x,t_now,y,hopt,cstr,inew,cnew

    cstr=dict(zip(list(f.constraints.keys()),[0.]*len(f.constraints)))# INITIALISATION
    if f.constraints!={}:
        for i in f.constraints.keys():
            if isinstance(f.constraints[i][1],tuple):
                test_exp,(init,_,_,_,_,_,name)=f.constraints[i]
            else:
                (init,_,_,_,_,_,name)=f.constraints[i]
                test_exp=lambda t:True
            ind=f.xnames.index(name)
            cstr[i]=np.where(test_exp(0.),init(x0[ind],0.,h0),cstr[i])

    if hasattr(f,'etat'):
        i0=f.etat
        if hasattr(f,'commande'):
            _,c0=f.commande(0.,T)
        else:
            c0=0
    else:
        i0=0
        c0=0
    y0=f.output(x0,0.,*P)
    _,_,_,xf,ts,yf,h,cstr,ifinal,_=while_loop(cond_fn,body_fn,
                                         (x0,0.,y0,x0,0.,y0,h0,cstr,i0,c0))
    if hasattr(f,'etat'):
        f.etat=ifinal
    if f.constraints!={}:
        for i in f.constraints.keys():
            if isinstance(f.constraints[i][1],tuple):
                _,(_,_,fin,_,_,_,_)=f.constraints[i]
            else:
                (_,_,fin,_,_,_,_)=f.constraints[i]
            cstr[i]=fin(ts,cstr[i],T)

    return (ts,xf,yf,cstr)


@_odeint45.defjvp
def _odeint45_jvp(f,h0,tol, primals, tangents):
    x0,T, *P = primals
    delta_x0,dT, *dP = tangents
    nPdP = len(P)

    def f_aug(x,delta_x, t, *P_and_dP):
        P, dP=P_and_dP[:nPdP],P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x, t, *P), (delta_x,
                                                            0., *dP))
        return tangent_dot

    xf,yf,cstr,ts,dts,xf_dot,yf_dot,cstr_dot=odeint45_etendu(f,f_aug,nPdP,h0,
                tol, x0,delta_x0,T,dT, *P, *dP)
    return (ts,xf,yf,cstr),(dts,xf_dot,yf_dot,cstr_dot)


def odeint45_etendu(f,f_aug,nPdP,h0,tol,x0,delta_x0,T,dT,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]
    type,cond_stop=f.stop

    def cond_fn(state):
        x_prev2,_,_,_,_,x_prev,delta_x_prev,_,_,t_prev, h,cstr,_,_,_ = state
        if type=='seuil':
            val,seuil=cond_stop(x_prev,f.xnames)
            valp,_ = cond_stop(x_prev2,f.xnames)
            return (h>0) & (np.sign(val-seuil)==np.sign(valp-seuil))
        else:
            return (h > 0) & cond_stop(t_prev,t_prev+h,cstr)


    def body_fn(state):
        _,_,_,_,_,x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev, h,cstr,\
                delta_cstr,i,c = state

        x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                        i,c,h,f,tol,h0,T,*P)

        if type=='seuil':
            output,seuil=cond_stop(x,f.xnames)
            outputprev,_=cond_stop(x_prev,f.xnames)
            x,hopt,_,_,t_now,_,y,_,_=cond(
                np.sign(output-seuil)!=np.sign(outputprev-seuil),interpolation,
                        lambda state:state,(x,hopt,x_prev,t_prev,t_now,y_prev,y,
                                            output-seuil,outputprev-seuil))
        elif isinstance(type,float):
            x=np.where(t_now>type,((x_prev-x)*type+t_prev*x-t_now*x_prev)
                       /(t_prev-t_now),x)
            y=np.where(t_now>type,((y_prev-y)*type+t_prev*y-t_now*y_prev)
                       /(t_prev-t_now),y)
            t_now,hopt=np.where(t_now>type,type,t_now),\
                       np.where(t_now>type,type-t_prev,hopt)

        delta_x=rk_step_der(x_prev,t_prev,delta_x_prev,h,f_aug,*P_and_dP)
        if hasattr(f,'computeotherX'):
            delta_x=jvp(f.computeotherX,(x,t_now,*P),(delta_x,0.,*dP))[1]
        delta_y=jvp(f.output,(x,t_now,*P),(delta_x,0.,*dP))[1]

        if f.constraints!={}:
            for i in f.constraints.keys():
                if isinstance(f.constraints[i][1], tuple):
                    test_exp,(_,expression,_,_,der_expression,_,name)=\
                        f.constraints[i]
                else:
                    (_,expression,_,_,der_expression,_,name)=f.constraints[i]
                    test_exp = lambda t: True
                ind=f.xnames.index(name)
                cstr[i] = np.where(test_exp(t_now),expression(t_prev,x_prev[ind],
                            t_now,x[ind], cstr[i],h,T),cstr[i])
                delta_cstr[i]= np.where(test_exp(t_now),der_expression(t_prev,
                    x_prev[ind],delta_x_prev[ind], t_now, x[ind],delta_x[ind],
                                    cstr[i],delta_cstr[i],h,T),delta_cstr[i])

        return x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,x,delta_x,y,\
               delta_y,t_now, hopt,cstr,delta_cstr,inew,cnew

    cstr=dict(zip(list(f.constraints.keys()),[0.]*len(f.constraints)))#INITIALISATION
    delta_cstr=dict(zip(list(f.constraints.keys()),[0.]*len(f.constraints)))
    if f.constraints!={}:
        for i in f.constraints.keys():
            if isinstance(f.constraints[i][1], tuple):
                test_exp,(init,_,_,dinit,_,_,name) = f.constraints[i]
            else:
                (init,_,_,dinit,_,_,name) = f.constraints[i]
                test_exp = lambda t: True
            ind=f.xnames.index(name)
            cstr[i]=np.where(test_exp(0.),init(x0[ind],0.,h0),
                             cstr[i])
            delta_cstr[i]=np.where(test_exp(0.),dinit(x0[ind],delta_x0[ind],0.,
                                    h0),delta_cstr[i])

    for element in f.__dict__.keys(): # pour eviter erreurs de code
        if hasattr(f.__dict__[element],'primal'):
            f.__dict__[element]=f.__dict__[element].primal
    if hasattr(f,'etat'):
        i0=f.etat
        if hasattr(f,'commande'):
            _,c0=f.commande(0.,T)
        else:
            c0=0
    else:
        i0=0
        c0=0
    y0=f.output(x0,0.,*P)
    delta_y0=jvp(f.output,(x0,0.,*P),(delta_x0,0.,*dP))[1]
    xfm1,_,_,_,_,xf,delta_xf,yf,delta_yf,ts,h,cstr,delta_cstr,ifinal,_=\
        while_loop(cond_fn,body_fn,(x0,delta_x0,y0,delta_y0,0.,x0,delta_x0,y0,
                                    delta_y0,0.,h0,cstr,delta_cstr,i0,c0))
    if hasattr(f,'etat'):
        f.etat=ifinal
    if f.constraints!={}:
        for i in f.constraints.keys():
            if isinstance(f.constraints[i][1],tuple):
                _,(_,_,fin,_,_,der_fin,name)=f.constraints[i]
            else:
                (_,_,fin,_,_,der_fin,name)=f.constraints[i]
            ind=f.xnames.index(name)
            cstr[i]=fin(ts,cstr[i],T)
            delta_cstr[i]=der_fin(ts,cstr[i],T,delta_cstr[i],dT,xf[ind])

    if type=='seuil': # partial derivatives of ts
        dout,_=cond_stop(delta_xf,f.xnames)
        xseuil,_=cond_stop(f.derivative(xf,ts,*P),f.xnames)
        dts=-(1/xseuil)*dout
    elif type=='rp':
        if hasattr(f,'topo_fixe'):
            f.compute_topo_fixe()
        ind_rp=f.xnames.index(f.last_var_bf_rp)
        xseuil=f.derivative(xf,ts,*P)[ind_rp]
        dts=-(1/xseuil)*delta_xf[ind_rp]
    else:
        dts=0.
    return xf,yf,cstr,ts,dts,delta_xf,delta_yf,delta_cstr


################################################################################
def T_pair(T):
    return lambda t:(t//T)%2==0

def T_impair(T):
    return lambda t:(t//T)%2!=0

def T_numero(T,n,i):
    return lambda t:(t//T)%n!=i

def Min(name):
    def init(x0,t0,h0):
        return x0
    def expression(t_prev,x_prev,t,x,cstr,h,_):
        return np.minimum(x,cstr)
    def fin(tchoc,cstr,_):
        return cstr
    def dinit(x0,dx0,t0,h0):
        return dx0
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,_):
        return np.where(np.minimum(cstr,x)==x,dx,dcstr)
    def dfin(tchoc,cstr,_,dcstr,dT,xf):
        return dcstr
    return init,expression,fin,dinit,dexpression,dfin,name

def Max(name):
    def init(x0,t0,h0):
        return x0
    def expression(t_prev,x_prev,t,x,cstr,h,_):
        return np.maximum(x,cstr)
    def fin(tchoc, cstr, _):
        return cstr
    def dinit(x0, dx0, t0, h0):
        return dx0
    def dexpression(t_prev, x_prev, dprev, t, x, dx, cstr, dcstr, h, _):
        return np.where(np.maximum(cstr,x)==x,dx,dcstr)
    def dfin(tchoc, cstr, _, dcstr, dT, xf):
        return dcstr
    return init, expression, fin, dinit, dexpression, dfin,name

def moy(name):
    def init(x0,t0,h0):
        return 0.
    def expression(t_prev, x_prev, t, x, cstr, h, _):
        return cstr+0.5*h*(x_prev+x)
    def fin(tchoc,cstr,_):
        return cstr/tchoc
    def dinit(x0,dx0,t0,h0):
        return 0.
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,_):
        return dcstr+0.5*h*(dprev+ dx)
    def dfin(tchoc,cstr,_,dcstr,dT,xf):
        return dcstr/tchoc
    return init, expression, fin, dinit, dexpression, dfin,name

def eff(name):
    def init(x0,t0,h0):
        return 0.
    def expression(t_prev,x_prev,t,x,cstr,h,_):
        return cstr+0.5*h*(x_prev**2+x**2)
    def fin(tchoc,cstr,_):
        return np.sqrt(cstr/tchoc)
    def dinit(x0,dx0,t0,h0):
        return 0.
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,_):
        return dcstr+0.5*h*(2*x_prev*dprev+2*x* dx)
    def dfin(tchoc,cstr,_,dcstr,dT,xf):
        return dcstr/(2*tchoc*cstr)
    return init, expression, fin, dinit, dexpression, dfin,name

def min_T(T,name):
    def init(x0,t0,h0):
        return x0
    def expression(t_prev,x_prev,t,x,cstr,h,_):
        return np.where((t_prev//T)==(t//T),np.minimum(x,cstr),x)
    def fin(tchoc,cstr,_):
        return cstr
    def dinit(x0,dx0,t0,h0):
        return dx0
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,_):
        return jvp(expression,(t_prev,x_prev,t,x,cstr,h,_),
                   (0.,dprev,0.,dx,dcstr,0.,0.))[1]#np.where((t_prev//T)==(t//T),np.where(np.minimum(cstr,
                #x)==x,dx,dcstr),dx)#
    def dfin(tchoc,cstr,_,dcstr,dT,xf):
        return dcstr
    return init, expression, fin, dinit, dexpression, dfin,name

def max_T(T,name):
    def init(x0,t0,h0):
        return x0
    def expression(t_prev,x_prev,t,x,cstr,h,_):
        return np.where((t_prev//T)==(t//T),np.maximum(x,cstr),x)
    def fin(tchoc,cstr,_):
        return cstr
    def dinit(x0,dx0,t0,h0):
        return dx0
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,_):
        return jvp(expression,(t_prev,x_prev,t,x,cstr,h,_),
                   (0.,dprev,0.,dx,dcstr,0.,0.))[1]#np.where((t_prev//T)==(t//T),np.where(np.maximum(cstr,
                #x)==x,dx,dcstr),dx)#
    def dfin(tchoc,cstr,_,dcstr,dT,xf):
        return dcstr
    return init, expression, fin, dinit, dexpression, dfin,name

def moy_T(name):
    def init(x0,t0,h0):
        return 0.
    def expression(t_prev,x_prev,t,x,cstr,h,T):
        return np.where((t_prev//T)==(t//T),cstr+0.5*h*(x_prev+x), 0.)
    def fin(tchoc,cstr,T):
        return cstr/T
    def dinit(x0,dx0,t0,h0):
        return 0.
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,T):
        return np.where((t_prev//T)==(t//T),dcstr+0.5*h*(dprev+dx),0.)
    def dfin(tchoc,cstr,T,dcstr,dT,xf):
        return dcstr/T+((xf-cstr)/T)*dT
    return init, expression, fin, dinit, dexpression, dfin,name

def eff_T(name):
    def init(x0,t0,h0):
        return 0.
    def expression(t_prev,x_prev,t,x,cstr,h,T):
        return np.where((t_prev//T)==(t//T),cstr+0.5*h*(x_prev**2+x**2),0.)
    def fin(tchoc,cstr,T):
        return np.sqrt(cstr/T)
    def dinit(x0,dx0,t0,h0):
        return 0.
    def dexpression(t_prev,x_prev,dprev,t,x,dx,cstr,dcstr,h,T):
        return np.where((t_prev//T)==(t//T),dcstr+0.5*h*(2*x_prev*
                                    dprev+2*x*dx),0.)
    def dfin(tchoc,cstr,T,dcstr,dT,xf):
        return dcstr/(2*T*cstr)+(xf**2-cstr**2)/(2*cstr*T)*dT
    return init, expression, fin, dinit, dexpression, dfin,name


def reg_perm(T,nbT,names_var,a=1e-5):
    constr = {}
    for i in range(len(names_var)):
        constr[names_var[i]+'_min']=(T_pair(nbT * T),
                                     min_T(nbT * T, names_var[i]))
        constr[names_var[i]+'_minimp']=(T_impair(nbT * T),
                                     min_T(nbT * T, names_var[i]))
        constr[names_var[i]+'_max']=(T_pair(nbT * T),
                                     max_T(nbT * T, names_var[i]))
        constr[names_var[i]+'_maximp']=(T_impair(nbT * T),
                                     max_T(nbT * T, names_var[i]))
    def regime_perm(t_prev,t,cstr):
        vectp,vectimp=np.zeros(2*len(names_var)),np.zeros(2*len(names_var))
        for i in range(len(names_var)):
            vectp=vectp.at[i].set(cstr[names_var[i]+'_min'])
            vectp=vectp.at[2*i+1].set(cstr[names_var[i]+'_max'])
            vectimp=vectimp.at[i].set(cstr[names_var[i]+'_minimp'])
            vectimp=vectimp.at[2*i+1].set(cstr[names_var[i]+'_maximp'])
        return np.bitwise_not(np.bitwise_and(np.allclose(vectp,vectimp,atol=a),
                    np.not_equal(t_prev//T,t//T)))
    return ('rp',regime_perm),constr

def seuil(ind,seuil=0.):
    return ('seuil', lambda x,names: (x[names.index(ind)], seuil))

def temps_final(tf):
    return (tf,lambda t_prev,t,cstr:t_prev<tf)

def get_indice(names,valeur,output):
    if len(output)==1:
        return valeur[names.index(output[0])]
    else:
        return (valeur[names.index(i)] for i in output)

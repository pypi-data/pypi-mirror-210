from noloadj.ODE.ode45_fft import odeint45_fft,odeint45_fft_etendu
from noloadj.ODE.ode_tools import *
from noloadj.ODE.ode45 import next_step_simulation,rk_step_der
from jax.lax import while_loop

def odeint45_extract_fft(f,x0,*P,M,T=0.,h0=1e-5,tol=1.48e-8):
    return _odeint45_extract_fft(f,h0,tol,M,x0,T,*P)


@partial(custom_jvp,nondiff_argnums=(0,1,2,3))
def _odeint45_extract_fft(f,h0,tol,M,x0,T,*P):
    type,cond_stop=f.stop

    def cond_fn(state):
        x_prev2,_,_,x_prev,t_prev,_,h,cstr,_,_=state
        return (h > 0) & cond_stop(t_prev,t_prev+h,cstr)
    def body_fn(state):
        _,_,_,x_prev,t_prev,y_prev,h,cstr,i,c=state

        x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                    i,c,h,f,tol,h0,T,*P)

        if isinstance(type,float):
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
    if hasattr(f,'topo_fixe'):
        f.compute_topo_fixe()
    ####################################################################### FFT
    freq_cstr=dict(zip(list(f.freq_constraints.keys()),
                                [0.] * len(f.freq_constraints)))
    if type=='rp':
        _,_,module,phase=odeint45_fft(f,xf,np.linspace(ts,ts+T,M),*P,
                                    M=M,T=T,h0=h0)
    else:
        _,_,module,phase=odeint45_fft(f,x0,np.linspace(0.,type,M),*P,M=M,T=T,
                                      h0=h0)

    vect_freq=np.where(M//2==0,np.linspace(0.,(M/2-1)/(M*h0),M//2),
                          np.linspace(0.,(M-1)/(2*M*h0),M//2))
    if f.freq_constraints!={}:
        for i in f.freq_constraints.keys():
            expression,_,name=f.freq_constraints[i]
            ind = f.xnames.index(name)
            freq_cstr[i]=expression(module[ind],phase[ind],vect_freq,1/T)

    return (ts,xf,yf,cstr,freq_cstr)


@_odeint45_extract_fft.defjvp
def _odeint45_fft_jvp(f,h0,tol,M, primals, tangents):
    x0,T, *P = primals
    delta_x0,dT, *dP = tangents
    nPdP = len(P)

    def f_aug(x0,delta_x0, t, *P_and_dP):
        P,dP =P_and_dP[:nPdP],P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x0, t, *P), (delta_x0,
                                                            0., *dP))
        return tangent_dot

    xf,yf,cstr,freq_cstr,ts,dts,xf_dot,yf_dot,cstr_dot,freq_cstr_dot=\
        odeint45_extract_fft_etendu(f,f_aug,nPdP,h0,tol,M,x0,delta_x0,T,dT,
                                    *P,*dP)
    return (ts,xf,yf,cstr,freq_cstr),(dts,xf_dot,yf_dot,cstr_dot,freq_cstr_dot)


def odeint45_extract_fft_etendu(f,f_aug,nPdP,h0,tol,M,x0,delta_x0,T,dT,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]
    type,cond_stop=f.stop

    def cond_fn(state):
        x_prev2,_,_,_,_,x_prev,delta_x_prev,_,_,t_prev, h,cstr,_,_,_ = state
        return (h > 0) & cond_stop(t_prev,t_prev+h,cstr)
    def body_fn(state):
        _,_,_,_,_,x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev, h,cstr,\
                delta_cstr,i,c = state

        x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                        i,c,h,f,tol,h0,T,*P)

        if isinstance(type,float):
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
                cstr[i] =np.where(test_exp(t_now),expression(t_prev,x_prev[ind],
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

    if type=='rp':
        if hasattr(f,'topo_fixe'):
            f.compute_topo_fixe()
        ind_rp=f.xnames.index(f.last_var_bf_rp)
        xseuil=f.derivative(xf,ts,*P)[ind_rp]
        dts=-(1/xseuil)*delta_xf[ind_rp]
    else:
        dts=0.
    ####################################################################### FFT
    freq_cstr=dict(zip(list(f.freq_constraints.keys()),
                       [0.]*len(f.freq_constraints)))
    freq_delta_cstr=dict(zip(list(f.freq_constraints.keys()),
                             [0.]*len(f.freq_constraints)))
    if type=='rp':
        _,_,module,phase,_,_,dmodule,dphase=odeint45_fft_etendu(f,f_aug,nPdP,h0,
                     tol,M,xf,delta_xf,np.linspace(ts,ts+T,M),T,*P_and_dP)
    else:
        _,_,module,phase,_,_,dmodule,dphase=odeint45_fft_etendu(f,f_aug,nPdP,h0,
                     tol,M,xf,delta_xf,np.linspace(0.,type,M),T,*P_and_dP)

    vect_freq=np.where(M//2==0,np.linspace(0.,(M/2-1)/(M*h0),M//2),
                          np.linspace(0.,(M-1)/(2*M*h0),M//2))
    if f.freq_constraints!={}:
        for i in f.freq_constraints.keys():
            _,der_expression,name=f.freq_constraints[i]
            ind = f.xnames.index(name)
            freq_cstr[i],freq_delta_cstr[i]=der_expression(module[ind],
                phase[ind],dmodule[ind], dphase[ind],vect_freq,1//T)

    return xf,yf,cstr,freq_cstr,ts,dts,delta_xf,delta_yf,delta_cstr,\
           freq_delta_cstr


################################################################################

def Module_0Hz(name):
    def expression(module,phase,vect_freq,f):
        res=module[0]
        return res
    def der_expression(module,phase,dmodule,dphase,vect_freq,f):
        res=module[0]
        dres=dmodule[0]
        return res,dres
    return expression,der_expression,name

def Module_Fondamental(name):
    def expression(module,phase,vect_freq,f):
        indf=np.argmin(np.abs(vect_freq-f))
        res=module[indf]
        return res
    def der_expression(module,phase,dmodule,dphase,vect_freq,f):
        indf=np.argmin(np.abs(vect_freq-f))
        res=module[indf]
        dres=dmodule[indf]
        return res,dres
    return expression,der_expression,name

def Module_Harmoniques(name,number):
    def expression(module,phase,vect_freq,f):
        res=np.zeros(number)
        for j in range(len(res)):
            indf=np.argmin(np.abs(vect_freq-(j+2)*f))
            res=res.at[j].set(module[indf])
        return res
    def der_expression(module,phase,dmodule,dphase,vect_freq,f):
        res = np.zeros(number)
        dres=np.zeros(number)
        for j in range(len(res)):
            indf=np.argmin(np.abs(vect_freq-(j+2)*f))
            res=res.at[j].set(module[indf])
            dres=dres.at[j].set(dmodule[indf])
        return res,dres
    return expression,der_expression,name

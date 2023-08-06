import jax.numpy as np
from jax.lax import *
from jax import custom_jvp,jvp,interpreters
from functools import partial

def odeint45(f,x0,t,*P,T=0.,h0=1e-5,tol=1.48e-8):
    return _odeint45(f,h0,tol,x0,t,T,*P)


def rk_step(x_prev, t_prev, h,f,*P):
    k1=f(x_prev, t_prev,*P)
    k2 = f(x_prev + h*0.2 * k1, t_prev + 0.2 * h,*P)
    k3 = f(x_prev + h*(3 * k1 + 9 * k2) / 40,t_prev + 3 * h / 10,*P)
    k4 = f(x_prev + h*(44 * k1 / 45 - 56 * k2 / 15 + 32 * k3 / 9),t_prev +
           4 * h / 5,*P)
    k5 = f(x_prev + h*(19372 * k1 / 6561 - 25360 * k2 / 2187 +
            64448 * k3 / 6561- 212 * k4 / 729),
           t_prev + 8 * h / 9,*P)
    k6 = f(x_prev + h*(9017 * k1 / 3168 - 355 * k2 / 33 + 46732 * k3 / 5247+
            49 * k4 / 176 - 5103 * k5 / 18656),t_prev + h,*P)
    k7 = f(x_prev + h*(35 * k1 / 384 + 500 * k3 / 1113 +
            125 * k4 / 192 -2187 * k5 / 6784 + 11 * k6 / 84),t_prev + h,*P)

    x = x_prev + h *(35 * k1 / 384 + 500 * k3 / 1113 + 125 * k4 / 192
             -2187 * k5 / 6784 + 11 * k6 / 84)
    xest = x_prev + h *(5179 * k1 / 57600 + 7571* k3 / 16695 + 393 * k4 /640
            - 92097 * k5 / 339200 + 187 * k6 / 2100 + k7 / 40)
    t_now = t_prev + h
    return x, xest, t_now


def optimal_step(x,xest,h,tol,errcon=1.89e-4):
    est=np.linalg.norm(x-xest)
    R = (est+1e-16) / h
    err_ratio = R / tol
    delta = (2*err_ratio)**(-0.2)
    h=np.where(est>=errcon,h*delta,1.0*h)
    return h


def interpolation(state):
    x,h,x_prev,t_prev,t_now,y_prev,y,var_seuil,var_seuil_prev=state
    tchoc=(-t_prev*var_seuil+t_now*var_seuil_prev)/(var_seuil_prev-var_seuil)
    h=tchoc-t_prev
    xchoc=(x_prev-x)*tchoc/(t_prev-t_now)+(t_prev*x-t_now*x_prev)/(t_prev-t_now)
    ychoc=(y_prev-y)*tchoc/(t_prev-t_now)+(t_prev*y-t_now*y_prev)/(t_prev-t_now)
    return xchoc,h,x_prev,t_prev,tchoc,y_prev,ychoc,var_seuil,var_seuil_prev

def interp_state_chgt(x_prev,y_prev,yb,t_prev,x,y,t_now,f,i,h,cnew):
    ind=np.where(np.array_equiv(y,yb),-1,np.argmax(np.abs(y-yb)))
    val_seuil=yb[ind]
    condition = np.bitwise_and(np.sign(x[ind]-val_seuil)!=np.sign(
            x_prev[ind]-val_seuil),np.not_equal(ind,-1))
    condition=np.bitwise_and(condition,np.bitwise_not(np.allclose(
            x_prev[ind]-val_seuil,0.)))
    x,h,_,_,t_now,_,y,_,_=cond(condition,interpolation,
                lambda state:state,(x,h,x_prev,t_prev,t_now,y_prev,y,
                                    x[ind]-val_seuil,x_prev[ind]-val_seuil))
    if hasattr(f,'commande'):
        _,x,y=f.update(x,y,t_now,i,cnew)
    else:
        _,x,y=f.update(x,y,t_now,i)
    return x,y,h,t_now

def next_step_simulation(x_prev,t_prev,y_prev,i,c,h,f,tol,h0,T,*P):
    if hasattr(f,'etat'):
        f.etat=i
    if hasattr(f,'topo_fixe'):
        f.compute_topo_fixe()
    x,xest,t_now=rk_step(x_prev,t_prev,h,f.derivative,*P)
    if hasattr(f,'computeotherX'):
        x=f.computeotherX(x,t_now,*P)
        xest=f.computeotherX(xest,t_now,*P)
    y=f.output(x,t_now,*P)
    hopt,cnew,tpdi=0.,0,0.
    if hasattr(f,'etat'):
        if hasattr(f,'commande'):
            tpdi,cnew=f.commande(t_now,T)
            inew,_,yb=f.update(x,y,t_now,i,cnew)
        else:
            cnew=c
            inew,_,yb=f.update(x,y,t_now,i)
        x,y,h,t_now=cond(inew!=i,lambda state:interp_state_chgt(x_prev,y_prev,
        yb,t_prev,x,y,t_now,f,i,h,cnew),lambda state:state,(x,y,h,t_now))

        y=f.output(x,t_now,*P)
        hopt = optimal_step(x,xest, h, tol)
        if hasattr(f,'commande'):
            hopt=np.minimum(tpdi-t_now,hopt)
        hopt=np.where(inew!=i,h0,hopt) # pour accelerer code
    else:
        inew=i
        cnew=c
    if hasattr(f,'event'):
        for e in f.event:
            name,signe_str,seuil,name2,chgt_etat=e
            var_seuil,var_seuil_prev=get_indice(f.xnames,x,[name]),\
                            get_indice(f.xnames,x_prev,[name])
            signe=np.where(signe_str=='<',-1,1)
            condition = np.bitwise_and(np.sign(var_seuil-seuil)==signe,
                       np.bitwise_not(np.allclose(var_seuil_prev-seuil,0.)))
            hopt = optimal_step(x, xest, h, tol)
            x,h,_,_,t_now,_,y,_,_=cond(condition,interpolation,
                lambda state:state,(x,h,x_prev,t_prev,t_now,y_prev,y,
                                    var_seuil-seuil,var_seuil_prev-seuil))
            xevent=cond(condition,chgt_etat,lambda state:state,
                                        get_indice(f.xnames,x,[name2]))
            x=x.at[f.xnames.index(name2)].set(xevent)
            y=f.output(x,t_now,*P)
    elif not hasattr(f,'event') and not hasattr(f,'etat'):
        hopt = optimal_step(x, xest, h, tol)
    return x,t_now,y,hopt,inew,cnew

@partial(custom_jvp,nondiff_argnums=(0,1,2))
def _odeint45(f,h0,tol,x0,t,T,*P):

    def scan_fun(state,t):

        def cond_fn(state):
            _,_,_,x_prev,t_prev,_,h,_,_=state
            return (t_prev<t) & (h>0)

        def body_fn(state):
            _,_,_,x_prev,t_prev,y_prev,h,i,c=state

            x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                    i,c,h,f,tol,h0,T,*P)

            return x_prev,t_prev,y_prev,x,t_now,y,hopt,inew,cnew

        x_prev,t_prev,y_prev,x_now,t_now,y_now,h,i,c = while_loop(cond_fn,
                                                                  body_fn,state)
        #interpolation lineaire
        x=((x_prev-x_now)*t+t_prev*x_now-t_now*x_prev)/(t_prev-t_now)
        y=((y_prev-y_now)*t+t_prev*y_now-t_now*y_prev)/(t_prev-t_now)
        return (x_prev,t_prev,y_prev,x,t,y,h,i,c),(x,y)

    if hasattr(f,'etat'):
        i0=f.etat
        if hasattr(f,'commande'):
            _,c0=f.commande(t[0],T)
        else:
            c0=0
    else:
        i0=0
        c0=0
    y0=f.output(x0,0.,*P)
    vect,(xs,ys)=scan(scan_fun,(x0,t[0],y0,x0,t[0],y0,h0,i0,c0),t[1:])
    if hasattr(f,'etat'):
        f.etat=vect[7]
    xs=np.transpose(np.concatenate((x0[None], xs)))
    ys=np.transpose(np.concatenate((y0[None], ys)))
    return xs,ys


@_odeint45.defjvp
def _odeint45_jvp(f,h0,tol, primals, tangents):
    x0, t,T, *P = primals
    delta_x0, _,_, *dP = tangents
    nPdP = len(P)

    def f_aug(x,delta_x, t, *P_and_dP):
        P, dP = P_and_dP[:nPdP], P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x, t, *P), (delta_x,
                                                    0., *dP))
        return tangent_dot

    xs,xs_dot,ys,ys_dot = odeint45_etendu(f,f_aug,nPdP,h0,tol, x0,delta_x0,
                                        t,T, *P, *dP)
    return (xs,ys),(xs_dot,ys_dot)

def rk_step_der(x_prev, t_prev, delta_x_prev,h,f_aug,*dP):
    k1 = f_aug(x_prev, delta_x_prev, t_prev, *dP)
    k2 = f_aug(x_prev, delta_x_prev + h * 0.2 * k1,t_prev + 0.2 * h , *dP)
    k3 = f_aug(x_prev, delta_x_prev + h * (3 * k1 + 9 * k2) / 40,t_prev
               +3 * h / 10, *dP)
    k4 = f_aug(x_prev,delta_x_prev + h*(44 * k1 / 45 - 56 * k2 /15+32*k3/9),
               t_prev + 4 * h / 5,*dP)
    k5 = f_aug(x_prev, delta_x_prev + h * (19372 * k1 / 6561 - 25360*k2/2187
                + 64448 * k3 / 6561 - 212 * k4 / 729),t_prev + 8 * h / 9, *dP)
    k6 = f_aug(x_prev,delta_x_prev+h*(9017 * k1 / 3168 -355 *k2/33 +46732*k3
            / 5247 + 49 * k4 / 176 - 5103 * k5 / 18656),t_prev + h, *dP)
    delta_x = delta_x_prev + h *(35 * k1 / 384 + 500 * k3 / 1113 +
            125 * k4 / 192 - 2187 * k5 / 6784 + 11 * k6 / 84)
    return delta_x


def odeint45_etendu(f,f_aug,nPdP,h0,tol,x0,delta_x0,t,T,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]

    def scan_fun(state, t):

        def cond_fn(state):
            _,_,_,_,_,x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,h,_,_=state
            return (t_prev < t) & (h > 0)

        def body_fn(state):
            _,_,_,_,_,x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,h,i,c=state

            x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                        i,c,h,f,tol,h0,T,*P)

            delta_x=rk_step_der(x_prev,t_prev,delta_x_prev,h,f_aug,*P_and_dP)
            if hasattr(f,'computeotherX'):
                delta_x=jvp(f.computeotherX,(x,t_now,*P),(delta_x,0.,*dP))[1]
            delta_y=jvp(f.output,(x,t_now,*P),(delta_x,0.,*dP))[1]

            return x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,x,delta_x,\
                   y,delta_y,t_now,hopt,inew,cnew

        x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,x_now,delta_x_now,y_now,\
          delta_y_now,t_now,h,i,c = while_loop(cond_fn, body_fn, state)
        # interpolation lineaire
        x = ((x_prev- x_now)*t+t_prev*x_now-t_now*x_prev)/(t_prev - t_now)
        delta_x = ((delta_x_prev-delta_x_now)*t+t_prev*delta_x_now-t_now*
                   delta_x_prev) / (t_prev - t_now)
        y = ((y_prev- y_now)*t+t_prev*y_now-t_now*y_prev)/(t_prev - t_now)
        delta_y = ((delta_y_prev-delta_y_now)*t+t_prev*delta_y_now-t_now*
                   delta_y_prev) / (t_prev - t_now)
        return (x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,x,delta_x,y,
                delta_y,t, h,i,c), (x,delta_x,y,delta_y)

    for element in f.__dict__.keys(): # pour eviter erreurs de code
        if hasattr(f.__dict__[element],'primal'):
            f.__dict__[element]=f.__dict__[element].primal
    if hasattr(f,'etat'):
        i0=f.etat
        if hasattr(f,'commande'):
            _,c0=f.commande(t[0],T)
        else:
            c0=0
    else:
        i0=0
        c0=0
    y0=f.output(x0,0.,*P)
    delta_y0=jvp(f.output,(x0,0.,*P),(delta_x0,0.,*dP))[1]
    vect,(xs,delta_xs,ys,delta_ys)=scan(scan_fun,(x0,delta_x0,y0,delta_y0,t[0],
                            x0,delta_x0,y0,delta_y0,t[0],h0,i0,c0),t[1:])
    if hasattr(f,'etat'):
        f.etat=vect[11]
    xs=np.transpose(np.concatenate((x0[None], xs)))
    ys=np.transpose(np.concatenate((y0[None], ys)))
    delta_xs=np.transpose(np.concatenate((delta_x0[None], delta_xs)))
    delta_ys = np.transpose(np.concatenate((delta_y0[None], delta_ys)))
    return xs,delta_xs,ys,delta_ys


def get_indice(names,valeur,output):
    if len(output)==1:
        return valeur[names.index(output[0])]
    else:
        return (valeur[names.index(i)] for i in output)
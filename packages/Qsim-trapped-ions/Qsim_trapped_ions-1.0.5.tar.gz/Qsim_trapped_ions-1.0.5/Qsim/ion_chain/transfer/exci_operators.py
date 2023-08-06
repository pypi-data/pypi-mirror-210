# -*- coding: utf-8 -*-
"""
Construct quantum operators used in excitation transfer systems 

@author: zhumj
"""
import numpy as np
import Qsim.operator.spin as spin
import Qsim.operator.phonon as phon
from  Qsim.ion_chain.ion_system import *
def summary():
    print("____________________________________________________________________")
    print("function: ph_list")
    print("Generate a list of phonon index used in computing laser-ion coupling")
    print("____________________________________________________________________")
    print("function: p_num")
    print("find the number of phonon spaces coupled to the laser")
    print("____________________________________________________________________")
    print("function: p_zero")
    print("Construct the zero operator on phonon spacer")
    print("____________________________________________________________________")
    print("function: p_I")
    print("Construct the identity operator on phonon space")
    print("____________________________________________________________________")
    print("function: p_ladder")
    print("Construct the ladder operator on phonon space")
    print("____________________________________________________________________")
    print("function: rho_thermal")
    print("Construct initial density matrix according to a thermal distribution")
    print("____________________________________________________________________")
    print("function: ini_state")
    print("Construct initial ket/density matrix that has integer phonon number")
    print("____________________________________________________________________")
    print("function: c_op")
    print("Construct the collapse operator for the transfer systems")
    print("____________________________________________________________________")
    print("function: spin_measure")
    print("Construct operators to measure spin evolution for excitation transfer")
    print("____________________________________________________________________")
    print("function: phonon_measure")
    print("Construct operators to measure phonon evolution for excitation transfer")
def ph_list(ion0):
    '''
    Generate a list of phonon index used in computing laser-ion coupling

    Parameters
    ----------
    ion0 : ion class object
    Returns
    -------
    list of int
    '''
    if ion0.df_phonon() [0]== 1: #only consider one phonon space
        mlist = ion0.active_phonon[0]
    else:   #two  phonon spaces
       mlist = ion0.active_phonon[ion0.df_laser]
    return mlist    

def pnum(ion0,df=None):
    '''
    find the number of phonon spaces coupled to the laser
    
    Parameters
    ----------
    ion0 : ion class object
    df : int, default as none
        vibrational degree of freedom that couples to the laser, 0: axial, 1: radial
        Specified if doing computations with a different coupling direction from the direction
        initialized in ion class object

    Returns
    -------
    int, number of phonon spaces coupled to the laser

    '''
    if df == None:
        df_couple = ion0.df_laser
    else:
        df_couple = df
    if ion0.df_phonon() [0]== 1: #only consider one phonon space
        dim = ion0.df_phonon()[1][0]
    else:   #two  phonon spaces
        dim = ion0.df_phonon()[1][df_couple]
    return dim    

def p_zero(ion0):
    '''
    construct the zero operator on phonon space
    Parameters
    ----------
    ion0 : ion class object

    Returns
    -------
    Qutip Operator

    '''
    Np = pnum(ion0)
    pcut =ion0.pcut
    if ion0.df_phonon()[0] == 1: #only consider one phonon space
        pzero = phon.zero_op(pcut[0],Np)
    else:     #two  phonon spaces
        pzero = tensor(phon.zero_op(pcut[0],ion0.df_phonon()[1][0]),
                       phon.zero_op(pcut[1],ion0.df_phonon()[1][1]))
    return pzero  

def p_I(ion0):
    '''
    construct the identity operator on phonon space
    Parameters
    ----------
    ion0 : ion class object

    Returns
    -------
    Qutip Operator

    '''
    Np = pnum(ion0)
    pcut =ion0.pcut
    if ion0.df_phonon()[0] == 1: #only consider one phonon space
        pI = phon.pI(pcut[0],Np)
    else:     #two  phonon spaces
        pI = tensor(phon.pI(pcut[0],ion0.df_phonon()[1][0]),
                    phon.pI(pcut[1],ion0.df_phonon()[1][1]))
    return pI

def p_ladder(ion0,mindex,atype,df=None):
    '''
    construct the ladder operator on phonon space
    Parameters
    ----------
    ion0 : ion class object
    mindex: int  
        index of phonon space where the ladder operator is acting on    
    atype: int 
        type of phonon operator, 0 for down, 1 for up
    df : int, default as none
         vibrational degree of freedom that couples to the laser, 0: axial, 1: radial
         Specified if doing computations with a different coupling direction from the direction
         initialized in ion class object    
    Returns
    -------
    Qutip Operator

    ''' 
    
    if df == None:
        df_couple = ion0.df_laser #use default
        Np = pnum(ion0)
    else:
        df_couple = df #specify the coupling coefficeint
        Np = pnum(ion0,df_couple)
    pcut = ion0.pcut
    if ion0.df_phonon()[0] == 1: #only consider one phonon space
        if atype == 0:
            opa = phon.down(mindex,pcut[0],Np)
        else:
            opa = phon.up(mindex,pcut[0],Np)
    else:     #two  phonon spaces
        if atype == 0:
            opa = phon.down(mindex,pcut[df_couple],Np)
        else:
            opa = phon.up(mindex,pcut[df_couple],Np)
        #construct in order axial, transverse
        if  df_couple ==0:
            opa = tensor(opa,phon.pI(pcut[1],ion0.df_phonon()[1][1]))
        else:
            opa = tensor(phon.pI(pcut[0],ion0.df_phonon()[1][0]),opa)
    return opa    

def rho_thermal(ion0,nbar_list,ket=False,s_num=0,):
    '''
    Construct initial density matrix/ket for pure state according to a thermal distribution
    Parameters
    ----------
    ion0: ions class object
       the object that represent the system to be simulated
    ket: bool, default as false
        if true, output state as ket for a pure superposition of fock states
        if false, output the usual density matrix used for thermal state
    s_num: list of int
        specify initial spin state, 0 for up, 1 of down, default as 0 
    nbar_list: list of list of float
        average phonon number of each phonon space
    Returns
    -------
    Qutip operator

    '''
    Ns = ion0.df_spin()
    isket = spin.spin_state(Ns,s_num)
    ini_sdm = isket*isket.dag()
    if ion0.df_phonon()[0] == 1: #only consider one phonon space
        for mindex in range(ion0.df_phonon()[1][0]):
            nbar = nbar_list[0][mindex]
            if mindex == 0:
                pho = phon.inip_thermal(ion0.pcut[0][0],nbar,ket)
            else:
                pho = tensor(pho,phon.inip_thermal(ion0.pcut[0][mindex],nbar,ket))
    else:
        for mindex in range(ion0.df_phonon()[1][0]):
            nbar = nbar_list[0][mindex]
            if mindex == 0:
                pho1 = phon.inip_thermal(ion0.pcut[0][0],nbar,ket)
            else:
                pho1 = tensor(pho1,phon.inip_thermal(ion0.pcut[0][mindex],nbar,ket))
        for mindex in range(ion0.df_phonon()[1][1]):
            nbar = nbar_list[1][mindex]
            if mindex == 0:
                pho2 = phon.inip_thermal(ion0.pcut[1][0],nbar,ket)
            else:
                pho2 = tensor(pho2,phon.inip_thermal(ion0.pcut[1][mindex],nbar,ket))        
    #dmat = fock(ion0.pcut,0)*fock(ion0.pcut,0).dag()
    #pho0 = tensor(dmat,dmat,dmat)
        pho = tensor(pho1,pho2)
    if ket:
        ket0 = tensor(isket,pho)
        return ket0
    else:
        rho0 = tensor(ini_sdm,pho)
        return rho0    

def ini_state(ion0,s_num,p_num,state_type):
    '''
    Construct initial ket/density matrix that has integer phonon number

    Parameters
    ----------
    ion0: ions class object
       the object that represent the system to be simulated
    s_num: list of int
        specify initial spin state, 0 for up, 1 of down
    p_num: list of list of int 
        specified phonon number for the state
    state_type: type of state to be generated 
        0 for density matrix
        1 for ket
    Returns
    -------
    Qutip operator

    '''
    Ns = ion0.df_spin()
    isket = spin.spin_state(Ns,s_num)
    ini_sdm = isket*isket.dag()
    if ion0.df_phonon()[0] == 1: #only consider one phonon space
        for m in range(ion0.df_phonon()[1][0]):
            if m == 0:
                pho = fock(ion0.pcut[0][0],p_num[0][m])
            else:
                pho = tensor(pho,phon.fock(ion0.pcut[0][m],p_num[0][m]))
    else:
        for m in range(ion0.df_phonon()[1][0]):
            if m == 0:
                pho1 = fock(ion0.pcut[0][0],p_num[0][m])
            else:
                pho1 = tensor(pho1,fock(ion0.pcut[0][m],p_num[0][m]))
        for m in range(ion0.df_phonon()[1][1]):
            if m == 0:
                pho2 = fock(ion0.pcut[1][0],p_num[1][m])
            else:
                pho2 = tensor(pho2,fock(ion0.pcut[1][m],p_num[1][m]))  
        pho = tensor(pho1,pho2)       
    dpmat = pho*pho.dag()
    rho0 = tensor(ini_sdm,dpmat)
    if state_type == 0:
        return rho0
    else:
        return tensor(isket,pho)

def c_op(ion0,nbar_list,normalized=True):
    '''
    Construct the collapse operator for the transfer systems
    Parameters
    ----------
    ion0 : ion class object
    nbar_list: list of float
        average phonon number of each phonon space
    normalized: bool
        if normalized, all cooling coefficient will be multiplied by
        corresponding Eigenmode matrix element
    Returns
    -------
    List of Qutip operator

    '''
    clist = []
    mindex = 0
    if ion0.df_laser == 0:
        emat = ion0.Axialmode()
    else:
        emat = ion0.Transmode()
    for m in ph_list(ion0):
        nbar = nbar_list[m]
        cm = tensor(spin.sI(ion0.df_spin()), p_ladder(ion0,mindex,0))
        if normalized:
            coeff = np.abs(emat[m,ion0.coolant[0]])*np.sqrt(fr_conv(ion0.gamma[m],'hz'))
        else:
            coeff = np.sqrt(fr_conv(ion0.gamma[m],'hz'))
        clist.append(coeff*np.sqrt(1+nbar)*cm)
        clist.append(coeff* np.sqrt(nbar)*cm.dag())
        mindex = mindex + 1                                            
    return clist

def spin_measure(ion0,s_config):
    '''
    Generate operators to measure spin evolution for excitation transfer systems

    Parameters
    ----------
    ion0 : ion class object
    index : list of int
        specify the spin state to be projected, 0 for spin up, 1 for spin down
        [0,1] means up, down state
    Returns
    -------
    s_op : Qutip operator

    '''
    s_ket = spin.spin_state(ion0.df_spin(),s_config)
    s_op = tensor(s_ket*s_ket.dag(), p_I(ion0))
    return s_op
def site_spin_measure(ion0,index):
    '''
    Generate operators to measure site spin population for excitation transfer systems
    p = 0.5*(<\sigma_z>)+0.5
    Parameters
    ----------
    ion0 : ion class object
    index : int
        specify the index of spin space to be measured
    Returns
    -------
    s_op : Qutip operator

    '''
    s_op = tensor( 0.5 * (spin.sI(ion0.df_spin()) + spin.sz(ion0.df_spin(),index)),
                  p_I(ion0))
    return s_op
def phonon_measure(ion0,mindex,df=None):
    '''
    Generate operators to measure phonon evolution for excitation transfer systems
    Parameters
    ----------
    ion0 : ion class object
    mindex: int  
        index of phonon space where the ladder operator is acting on    
    df : int, default as none
         vibrational degree of freedom that couples to the laser, 0: axial, 1: radial
         Specified if doing computations with a different coupling direction from the direction
         initialized in ion class object    
    Returns
    -------
    Qutip operator.

    '''
    if df == None:
        p_op = p_ladder(ion0,mindex,1)*p_ladder(ion0,mindex,0)
    else:     
        p_op = p_ladder(ion0,mindex,1,df)*p_ladder(ion0,mindex,0,df)
    p_op = tensor(spin.sI(ion0.df_spin()),p_op)
    return p_op    

def pstate_measure(ion0,slevel,mindex,df=None):
    '''
    mearsure the population of n=pcut state of a specific phonon space 
    in order to check the validity using a finite phonon space
    ion0 : ion class object
    slevel: int
        phonon state level to be measured    
    mindex: int  
        index of phonon space to be measured    
    df : int, default as none
         vibrational degree of freedom that couples to the laser, 0: axial, 1: radial
         Specified if doing computations with a different coupling direction from the direction
         initialized in ion class object    
    Returns
    -------
    Qutip operator.
    '''
    if df == None:
        df_couple = ion0.df_laser #use default
        Np = pnum(ion0)
    else:
        df_couple = df #specify the coupling direction
        Np = pnum(ion0, df_couple)
    pcut = ion0.pcut
    if ion0.df_phonon()[0] == 1: #only consider one phonon space
        opa = phon.state_measure(pcut[0],Np,slevel,mindex)
    else:     #two  phonon spaces
        opa = phon.state_measure(pcut[df_couple],Np,slevel,mindex)
        #construct in order axial, transverse
        if  df_couple ==0:
            opa = tensor(opa,phon.pI(pcut[1],ion0.df_phonon()[1][1]))
        else:
            opa = tensor(phon.pI(pcut[0],ion0.df_phonon()[1][0]),opa)
    return tensor(spin.sI(ion0.df_spin()),opa)   
    

    
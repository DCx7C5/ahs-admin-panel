import React, {use, useRef, useState} from "react";
import useCryptography from "../hooks/useCryptography";
import {DataContext} from "../components/DataProvider";

export const Test: React.FC = () => {
    const { password1, password2 } = useRef({
        password1: 'PASSWORD',
        password2: 'PASSWORD2',

    }).current;
    const [{privateKey1, publicKey1}, setKeyPair1] = useState({privateKey1: null, publicKey1: null});
    const [{privateKey2, publicKey2}, setKeyPair2] = useState({privateKey2: null, publicKey2: null});

    const {
        cryptoClient,
        isAuthenticated,
        isSuperUser
    } = use(DataContext)

    return (
        <div>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                <h4 className={'key'}>Authenticated:</h4>
                <div className={'value'}>{isAuthenticated ? 'yes' : 'no'}</div>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                <h4 className={'key'}>SuperUser:</h4>
                <div className={'value'}>{isSuperUser ? 'yes' : 'no'}</div>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                <h4 className={'key'}>Salt:</h4>
                <div className={'value'}>{}</div>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                <h4 className={'key'}>Password:</h4>
                <div className={'value'}>{password1}</div>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                <h4 className={'key'}>Password2:</h4>
                <div className={'value'}>{password2}</div>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                <h4 className={'key'}>PrivateKey1:</h4>
                <div className={'value'}>{}</div>
            </div>
        </div>
    )
}

export default Test;
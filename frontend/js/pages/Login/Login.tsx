import React, {lazy, Suspense, use, useEffect, useState} from "react";
import "@/../css/register.scss";
import TabNavigation from "../../components/tabs/TabNavigation";


const KeybaseAuthentication = lazy(() => import("./KeybaseAuthentication")
    .then(module => ({
      default: module.KeybaseAuthentication,
    }))
)

const WebAuthnAuthentication = lazy(() => import("./WebAuthnAuthentication")
    .then(module => ({
      default: module.WebAuthnAuthentication,
    }))
)


export const Login: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("WebAuthn");


  useEffect(() => {
      console.log('login mounted')
  }, []);

  return (
    <div className="text-center min-vh-100 max-vh-100" id="auth-wrap">
        <div className="auth-content" >
            <Suspense>
                <TabNavigation tabs={['WebAuthn', 'KeyBase']}
                               activeTab={activeTab}
                               setActiveTab={setActiveTab}
                />
                {activeTab === 'WebAuthn' && <WebAuthnAuthentication />}
                {activeTab === 'KeyBase' && <KeybaseAuthentication />}
            </Suspense>
        </div>
    </div>
  );
};


export default Login;

import React, {
    lazy,
    Suspense,
    use,
    useActionState,
    useCallback,
    useEffect,
    useOptimistic,
    useRef,
    useState
} from "react";
import { DataContext } from "../../components/DataProvider";
import "@/../css/register.scss";
import TabNavigation, {TabNavigationProps} from "../../components/tabs/TabNavigation";




const KeybaseRegistration = lazy(() => import("./KeybaseRegistration")
    .then(module => ({
      default: module.KeybaseRegistration,
    }))
)

const WebAuthnRegistration = lazy(() => import("./WebAuthnRegistration")
    .then(module => ({
      default: module.WebAuthnRegistration,
    }))
)


export const Registration: React.FC = () => {
  const {apiCli} = use(DataContext);

  const [activeTab, setActiveTab] = useState<string>("WebAuthn");


  useEffect(() => {
      console.log('registration mounted', apiCli)
  }, []);


  return (
    <div className="text-center min-vh-100 max-vh-100" id="auth-wrap">
        <div className="auth-content" >
            <Suspense>
                <TabNavigation tabs={['WebAuthn', 'KeyBase']}
                               activeTab={activeTab}
                               setActiveTab={setActiveTab}
                />
                {activeTab === 'WebAuthn' && <WebAuthnRegistration />}
                {activeTab === 'KeyBase' && <KeybaseRegistration />}
            </Suspense>
        </div>
    </div>
  );
};


export default Registration;

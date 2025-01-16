import { useState, useEffect } from 'react';



const useBreakPoint = () => {
    const [screenSize, setScreenSize] = useState(getCurrentBreakpoint());

    function getCurrentBreakpoint() {
        const width = window.innerWidth;
        if (width < 480) return 'xs';
        if (width < 768) return 'sm';
        if (width < 1024) return 'md';
        if (width < 1280) return 'lg';
        return 'xl';
    }

    useEffect(() => {
        const handleResize = () => {
            setScreenSize(getCurrentBreakpoint());
        };

        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return screenSize;
};

export default useBreakPoint;
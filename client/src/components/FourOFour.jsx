import React from 'react';
import * as myPath from '../js/myPath';

function FourOFour()
{
    const TIMEOUT = 3000; // given in milliseconds
    
    return (
    <div className="center">
        <h1>
            404 &mdash; Not Found
        </h1>
        <p>
            You will be redirected to main page
            in {`${Math.round(TIMEOUT / 1000)}`} seconds.
        </p>
        <script>
            { 
                
                setTimeout( () => {
                    window.location.pathname = myPath.getRootPath();
                    }, TIMEOUT)
            }
        </script>
    </div> );
}

export default FourOFour;
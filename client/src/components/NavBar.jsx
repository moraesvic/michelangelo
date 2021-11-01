import "./NavBar.css";
import * as myPath from "../js/myPath";

function ReminderDevMode(props)
{
    if (!process.env.NODE_ENV || process.env.NODE_ENV === 'development')
        return (
            <div className="reminder-dev-mode">
                ⚠️ You are in development mode ⚠️
            </div>
        );
    return null;
}

function NavBar(props) {
    /*
    props.dropdowns : list with JSON objects, each of which has a "title" and an
        "endpoint" property
    props.title : website title
    */
    if (!props.dropdowns || !props.title)
        return (null);

    let dropdownIndex = 0;
    
    return (
    <div className="nav-bar-wrapper">
    <nav className="nav-bar">
    
        <div className="nav-title">
            <a href={myPath.getRootPath()}>{props.title}</a>
            <a href="/">naive root</a>
        </div>
        { props.dropdowns.map( dropdown => {
            return (
                <div className="nav-item" key={`nav-item-${dropdownIndex++}`}>
                    <a href={myPath.linkTo(dropdown.endpoint)}>{dropdown.title}</a>
                </div>
            );
        })}
    </nav>
    <ReminderDevMode />
    </div>
    );
}

export default NavBar;
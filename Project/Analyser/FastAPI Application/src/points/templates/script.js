let names = ['head', 'trunk', 'right_arm', 'left_arm', 'right_leg', 'left_leg']
let legend_names = ['Head', 'Trunk', 'Right Arm', 'Left Arm', 'Right Leg', 'Left Leg']
let traces = names.map(name => {
    return {
        x: [],
        y: [],
        mode: 'lines+markers',
        type: 'scatter',
        name: legend_names[names.indexOf(name)]
    }
});
let graphs = ['x-y', 'y-x', 'x-time', 'y-time']
let graph_traces = {
    'x-y': structuredClone(traces),
    'y-x': structuredClone(traces),
    'x-time': structuredClone(traces),
    'y-time': structuredClone(traces)
}

let x_y_layout = {
    title: 'Real-Time Graph X vs Y',
    xaxis: {title: 'Y Axis'},
    yaxis: {title: 'X Axis'}
};
Plotly.newPlot('x-y-chart', graph_traces['x-y'], x_y_layout);

let y_x_layout = {
    title: 'Real-Time Graph Y vs X',
    xaxis: {title: 'X Axis'},
    yaxis: {title: 'Y Axis'}
};
Plotly.newPlot('y-x-chart', graph_traces['y-x'], y_x_layout);

let x_time_layout = {
    title: 'Real-Time Graph X vs Time',
    xaxis: {title: 'Time'},
    yaxis: {title: 'X Axis'}
};
Plotly.newPlot('x-time-chart', graph_traces['x-time'], x_time_layout);

let y_time_layout = {
    title: 'Real-Time Graph Y vs Time',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Y Axis'}
};
Plotly.newPlot('y-time-chart', graph_traces['y-time'], y_time_layout);

function fetchNewPoints() {
    fetch(`/skeleton/points/new?last_point_id=${lastSkeletonId}`)
        .then(response => response.json())
        .then(data => {
            let skeletons = data.skeleton_points;
            let trace_id;
            if (skeletons.length === 0) {
                if (data['last_point'] !== undefined) {
                    lastSkeletonId = data['last_point'];
                    initialSkeletonId = lastSkeletonId;
                }
            }
            for (let skeleton of skeletons) {
                let newPoints = skeleton.parts;
                let datetime = skeleton.datetime;
                lastSkeletonId = skeleton.id;
                if (newPoints.length > 0) {
                    if(initialSkeletonId === 0){
                        initialSkeletonId = lastSkeletonId;
                    }
                    for (let point of newPoints) {
                        trace_id = names.indexOf(point.part_type);
                        // x-y chart update
                        graph_traces['x-y'][trace_id].x.push(point.y);
                        graph_traces['x-y'][trace_id].y.push(point.x);
                        // y-x chart update
                        graph_traces['y-x'][trace_id].x.push(point.x);
                        graph_traces['y-x'][trace_id].y.push(point.y);
                        // x-time chart update
                        graph_traces['x-time'][trace_id].x.push(datetime);
                        graph_traces['x-time'][trace_id].y.push(point.x);
                        // y-time chart update
                        graph_traces['y-time'][trace_id].x.push(datetime);
                        graph_traces['y-time'][trace_id].y.push(point.y);
                    }
                    // Plotly.update('graph', traces, layout);
                    Plotly.update('x-y-chart', graph_traces['x-y'], x_y_layout);
                    Plotly.update('y-x-chart', graph_traces['y-x'], y_x_layout);
                    Plotly.update('x-time-chart', graph_traces['x-time'], x_time_layout);
                    Plotly.update('y-time-chart', graph_traces['y-time'], y_time_layout);
                }
            }
        });
}

let interval = 100;
let updateDataInterval = setInterval(fetchNewPoints, interval);


function refreshData(){
    // remove all currently displayed data in any of the charts
    for (let name of names){
        graph_traces['x-y'][names.indexOf(name)].x = [];
        graph_traces['x-y'][names.indexOf(name)].y = [];
        graph_traces['y-x'][names.indexOf(name)].x = [];
        graph_traces['y-x'][names.indexOf(name)].y = [];
        graph_traces['x-time'][names.indexOf(name)].x = [];
        graph_traces['x-time'][names.indexOf(name)].y = [];
        graph_traces['y-time'][names.indexOf(name)].x = [];
        graph_traces['y-time'][names.indexOf(name)].y = [];
    }
    Plotly.update('x-y-chart', graph_traces['x-y'], x_y_layout);
    Plotly.update('y-x-chart', graph_traces['y-x'], y_x_layout);
    Plotly.update('x-time-chart', graph_traces['x-time'], x_time_layout);
    Plotly.update('y-time-chart', graph_traces['y-time'], y_time_layout);
    lastSkeletonId = 0;
}

function toggleData(){
    let button = document.getElementById("toggle-data-btn");
    if (button.getAttribute('data-stopped') === 'true'){
        button.setAttribute('data-stopped', 'false');
        button.classList.remove('reverse');
        button.classList.add('delete');
        button.innerHTML = 'Stop data';
        refreshData();
        updateDataInterval = setInterval(fetchNewPoints, interval);
    } else {
        button.setAttribute('data-stopped', 'true');
        button.classList.remove('delete');
        button.classList.add('reverse');
        button.innerHTML = 'Start data';
        clearInterval(updateDataInterval);
    }
}

function saveDataToDocument(event){
    event.preventDefault();
    let message = document.getElementById('form-error-message');
    message.style.display = 'none';
    let form = document.getElementById('save-data-form');
    document.getElementById('first_skeleton_id').value = initialSkeletonId;
    document.getElementById('last_skeleton_id').value = lastSkeletonId;
    if (initialSkeletonId === lastSkeletonId){
        message.innerHTML = 'No data to save';
        message.style.display = 'block';
        return false;
    } else if (document.getElementById('new_document_name').value === ''){
        message.innerHTML = 'Document name cannot be empty';
        message.style.display = 'block';
        return false;
    }
    form.submit();
}

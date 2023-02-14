var interval = 1;
var counter = 0;

bar_chart_option = {
    maintainAspectRatio: false,
    plugins: {
      legend: false
    },
    scales: {
        y: {
            beginAtZero: true
        }
    }
}

line_chart_option = {
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    elements: {
        point:{
            radius: 0
        }
    }
}

line_chart_labels = [0, 5, 10, 15, 20, 25, 30];

traffic_flow_pedestrians = [0, 0, 0, 0, 0, 0, 0];
traffic_flow_vehicles = [0, 0, 0, 0, 0, 0, 0];
traffic_flow_bike = [0, 0, 0, 0, 0, 0, 0];

traffic_flow_collisions = [0, 0, 0, 0, 0, 0, 0];
traffic_flow_near_miss = [0, 0, 0, 0, 0, 0, 0];

const traffic_flow = document.getElementById('traffic-flow');
const collision_and_near_miss = document.getElementById('collision-and-near-miss');
const traffic_analysis = document.getElementById('traffic-analysis');
const collision_and_near_miss_analysis = document.getElementById('collision-and-near-miss-analysis');

const traffic_analysis_bar_chart = new Chart(traffic_analysis, {
    type: 'bar',
    data: {
        labels: ['Pedestrians', 'Vehicles', 'Bike'],
        datasets: [{
            label: 'Traffic Analysis',
            data: [0, 0, 0],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: bar_chart_option
});

const collision_and_near_miss_bar_chart = new Chart(collision_and_near_miss, {
    type: 'bar',
    data: {
        labels: ['Collisions', 'Near Miss'],
        datasets: [{
            label: 'Collision and Near Miss',
            data: [0, 0],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: bar_chart_option
});

const traffic_flow_line_chart = new Chart(traffic_flow, {
    type: 'line',
    data: {
      labels: line_chart_labels,
      datasets: [
        {
          label: 'Pedestrians',
          data: traffic_flow_pedestrians,
          borderColor: 'rgba(255, 99, 132, 0.8)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.2,
          fill: {
            target: 'origin',
            above: 'rgba(255, 99, 132, 0.1)',
          }
        },
        {
          label: 'Vehicles',
          data: traffic_flow_vehicles,
          borderColor: 'rgba(54, 162, 235, 0.8)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.2,
          fill: {
            target: 'origin',
            above: 'rgba(54, 162, 235, 0.1)',
          }
        },
        {
          label: 'Bike',
          data: traffic_flow_bike,
          borderColor: 'rgba(255, 206, 86, 0.8)',
          backgroundColor: 'rgba(255, 206, 86, 0.1)',
          tension: 0.2,
          fill: {
            target: 'origin',
            above: 'rgba(255, 206, 86, 0.1)',
          }
        }
      ]
    },
    options: line_chart_option
});

collision_and_near_miss_analysis_line_chart = new Chart(collision_and_near_miss_analysis, {
    type: 'line',
    data: {
      labels: line_chart_labels,
      datasets: [
        {
          label: 'collisions',
          data: traffic_flow_collisions,
          borderColor: 'rgba(255, 99, 132, 0.8)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.2,
          fill: {
            target: 'origin',
            above: 'rgba(255, 99, 132, 0.1)',
          }
        },
        {
          label: 'near_miss',
          data: traffic_flow_near_miss,
          borderColor: 'rgba(54, 162, 235, 0.8)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.2,
          fill: {
            target: 'origin',
            above: 'rgba(54, 162, 235, 0.1)',
          }
        }
      ]
    },
    options: line_chart_option
});


function updater() {

    // Get image src url & split it query params part
    var src = document.getElementById("inferred-stream").src
    var params = new URLSearchParams(src.split("/?")[1])
    // Get process id & file from params
    var id = params.get('process')
    var name = params.get('file')
    var url = `/data/?id=${id}`

    $.get(url, function(response, status) {
        data = response['data']

        // Get data from response
        near_miss = data['near_miss']
        collisions = data['collisions']
        pedestrians = data['pedestrians']
        vehicles = data['vehicles']
        bikes = data['bikes']

        // Update documents
        $('#collision-count').html(collisions);
        $('#pedestrian-count').html(pedestrians);
        $('#vehicle-count').html(vehicles);
        $('#bike-count').html(bikes);


        if(counter > line_chart_labels.length - 1){
            label = line_chart_labels.slice(-1).pop() + interval;
            line_chart_labels.push(label);
            traffic_flow_pedestrians.push(pedestrians);
            traffic_flow_vehicles.push(vehicles);
            traffic_flow_bike.push(bikes);
            traffic_flow_collisions.push(collisions);
            traffic_flow_near_miss.push(near_miss);
        } else {
            traffic_flow_pedestrians[counter] = pedestrians
            traffic_flow_vehicles[counter] = vehicles
            traffic_flow_bike[counter] = bikes
            traffic_flow_collisions[counter] = collisions
            traffic_flow_near_miss[counter] = near_miss
        }

        traffic_flow_line_chart.data.labels = line_chart_labels
        traffic_flow_line_chart.data.datasets[0].data = traffic_flow_pedestrians
        traffic_flow_line_chart.data.datasets[1].data = traffic_flow_vehicles
        traffic_flow_line_chart.data.datasets[2].data = traffic_flow_bike

        collision_and_near_miss_analysis_line_chart.data.labels = line_chart_labels
        collision_and_near_miss_analysis_line_chart.data.datasets[0].data = traffic_flow_collisions
        collision_and_near_miss_analysis_line_chart.data.datasets[1].data = traffic_flow_near_miss

        traffic_analysis_bar_chart.data.datasets[0].data = [pedestrians, vehicles, bikes]
        collision_and_near_miss_bar_chart.data.datasets[0].data = [collisions, near_miss]

        traffic_analysis_bar_chart.update();
        collision_and_near_miss_bar_chart.update();
        traffic_flow_line_chart.update();
        collision_and_near_miss_analysis_line_chart.update();


        counter += 1;
    });

};

updater();

setInterval(updater, interval * 1000);

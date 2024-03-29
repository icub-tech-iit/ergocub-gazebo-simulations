clc
clear

%% Modify this array to change the joints that will be plotted
joints_to_plot = ["r_shoulder_pitch" "r_elbow" "r_wrist_prosup"];

%% Start time of the plot
start_time = 22;

%% Modify these two variables affect the title in the plots
box_weight = 5.0;
increase_factor = 1.0;

%% Read mat files
testfiledir = './telemetry_data';
matfiles = dir(fullfile(testfiledir, '*.mat'));
nfiles = length(matfiles);
data  = cell(nfiles);

for i = 1 : nfiles
   data{i} = load( fullfile(testfiledir, matfiles(i).name) );
end

if nfiles == 0
    return
end

timestamp_encoders = [];
encoders = [];
timestamp_velocity = [];
velocity = [];
timestamp_torque = [];
torque = [];

%% Concatenate the data across files
for i = 1 : nfiles
    % Encoders
    timestamp_encoders = [timestamp_encoders  data{i}.measured_data.encoders.timestamps];
    encoders = [encoders squeeze(data{i}.measured_data.encoders.data)];
    % Velocity
    timestamp_velocity = [timestamp_velocity  data{i}.measured_data.velocity.timestamps];
    velocity = [velocity squeeze(data{i}.measured_data.velocity.data)];
    % Torque
    timestamp_torque = [timestamp_torque  data{i}.measured_data.torque.timestamps];
    torque = [torque squeeze(data{i}.measured_data.torque.data)];
end

%% Discriminate only the selected joints
description_list = data{1}.measured_data.description_list;
[description_list_size, ~] = size(description_list);
description_list_array = [];
for i = 1 : description_list_size
    description_list_array = [description_list_array; convertCharsToStrings(cell2mat(description_list(i)))];
end

[indices_to_plot, ~] = find(description_list_array==joints_to_plot);

%% Normalize timestamps
timestamp_encoders = timestamp_encoders - timestamp_encoders(1,1);
timestamp_velocity = timestamp_velocity - timestamp_velocity(1,1);
timestamp_torque   = timestamp_torque - timestamp_torque(1,1);

tmp = find(timestamp_encoders > start_time);
start_index_encoders = tmp(1);

tmp = find(timestamp_velocity > start_time);
start_index_velocity = tmp(1);

tmp = find(timestamp_torque > start_time);
start_index_torque = tmp(1);

%% Plot
title_prefix = strcat("x",num2str(increase_factor)," stickBot, box ", num2str(box_weight), "kg");
figure
plot(timestamp_encoders(start_index_encoders:end), encoders(indices_to_plot,start_index_encoders:end), 'LineWidth', 2)
title(strcat(title_prefix, " encoders"))
legend(joints_to_plot, 'Interpreter', 'None')
xlim([timestamp_encoders(start_index_encoders) max(timestamp_encoders)])
xlabel('Time [s]')
ylabel('Encoders [deg]')

figure
plot(timestamp_velocity(start_index_velocity:end), velocity(indices_to_plot,start_index_velocity:end), 'LineWidth', 2)
title(strcat(title_prefix, " velocity"))
legend(joints_to_plot, 'Interpreter', 'None')
xlim([timestamp_velocity(start_index_velocity) max(timestamp_velocity)])
xlabel('Time [s]')
ylabel('Velocity [deg/s]')

figure
plot(timestamp_torque(start_index_torque:end), torque(indices_to_plot,start_index_torque:end), 'LineWidth', 2)
title(strcat(title_prefix, " torque"))
legend(joints_to_plot, 'Interpreter', 'None')
xlim([timestamp_torque(start_index_torque) max(timestamp_torque)])
xlabel('Time [s]')
ylabel('Torque [Nm]')

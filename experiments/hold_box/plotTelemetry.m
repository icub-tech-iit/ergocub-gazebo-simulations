clc
clear

%% Modify this array to change the joints that will be plotted
joints_to_plot = ["r_shoulder_pitch" "r_elbow" "r_wrist_prosup"];

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
    timestamp_encoders = [timestamp_encoders  data{i}.hold_box.encoders.timestamps];
    encoders = [encoders squeeze(data{i}.hold_box.encoders.data)];
    % Velocity
    timestamp_velocity = [timestamp_velocity  data{i}.hold_box.velocity.timestamps];
    velocity = [velocity squeeze(data{i}.hold_box.velocity.data)];
    % Torque
    timestamp_torque = [timestamp_torque  data{i}.hold_box.torque.timestamps];
    torque = [torque squeeze(data{i}.hold_box.torque.data)];
end

%% Discriminate only the selected joints
description_list = data{1}.hold_box.description_list;
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
title_prefix = strcat("x",num2str(increase_factor)," stickBot, box ", num2str(box_weight), "kg");


%% Plot
figure
plot(timestamp_encoders, encoders(indices_to_plot,:), 'LineWidth', 2)
title(strcat(title_prefix, " encoders"))
legend(joints_to_plot, 'Interpreter', 'None')
xlim([0 max(timestamp_encoders)])
xlabel('Time [s]')
ylabel('Encoders [deg]')

figure
plot(timestamp_velocity, velocity(indices_to_plot,:), 'LineWidth', 2)
title(strcat(title_prefix, " velocity"))
legend(joints_to_plot, 'Interpreter', 'None')
xlim([0 max(timestamp_velocity)])
xlabel('Time [s]')
ylabel('Velocity [deg/s]')

figure
plot(timestamp_torque, torque(indices_to_plot,:), 'LineWidth', 2)
title(strcat(title_prefix, " torque"))
legend(joints_to_plot, 'Interpreter', 'None')
xlim([0 max(timestamp_torque)])
xlabel('Time [s]')
ylabel('Torque [Nm]')

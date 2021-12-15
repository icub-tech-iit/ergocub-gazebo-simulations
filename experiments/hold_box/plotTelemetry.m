clc
clear
% Read mat files
box_weight = 5.0;
increase_factor = 1.0;
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

description_list = data{1}.hold_box.description_list;
timestamp_encoders = [];
encoders = [];
timestamp_velocity = [];
velocity = [];
timestamp_torque = [];
torque = [];
% Concatenate the data across files
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

% Normalize timestamps
timestamp_encoders = timestamp_encoders - timestamp_encoders(1,1);
timestamp_velocity = timestamp_velocity - timestamp_velocity(1,1);
timestamp_torque   = timestamp_torque - timestamp_torque(1,1);
title_prefix = strcat("x",num2str(increase_factor)," stickBot, box ", num2str(box_weight), "kg");
% Plot
figure
plot(timestamp_encoders, encoders, 'LineWidth', 1)
title(strcat(title_prefix, " encoders"))
legend(description_list, 'Interpreter', 'None')
xlim([0 max(timestamp_encoders)])
xlabel('Time [s]')
ylabel('Encoders [deg]')

figure
plot(timestamp_velocity, velocity, 'LineWidth', 1)
title(strcat(title_prefix, " velocity"))
legend(description_list, 'Interpreter', 'None')
xlim([0 max(timestamp_velocity)])
xlabel('Time [s]')
ylabel('Velocity [deg/s]')

figure
plot(timestamp_torque, torque, 'LineWidth', 1)
title(strcat(title_prefix, " torque"))
legend(description_list, 'Interpreter', 'None')
xlim([0 max(timestamp_torque)])
xlabel('Time [s]')
ylabel('Torque [Nm]')

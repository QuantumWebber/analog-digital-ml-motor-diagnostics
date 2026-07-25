`timescale 1ns/1ps

module tb_fault_detect;

    localparam DATA_WIDTH  = 12;
    localparam WINDOW_SIZE = 64;    // small window for fast simulation
    localparam THRESHOLD   = 400;
    localparam FAULT_LIMIT = 20;

    reg clk = 0;
    reg rst_n = 0;
    reg sample_valid = 0;
    reg signed [DATA_WIDTH-1:0] sample_in = 0;

    wire fault_flag;
    wire [15:0] exceed_count;
    wire window_done;

    integer i;

    fault_detect #(
        .DATA_WIDTH (DATA_WIDTH),
        .THRESHOLD  (THRESHOLD),
        .WINDOW_SIZE(WINDOW_SIZE),
        .FAULT_LIMIT(FAULT_LIMIT)
    ) dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .sample_valid(sample_valid),
        .sample_in   (sample_in),
        .fault_flag  (fault_flag),
        .exceed_count(exceed_count),
        .window_done (window_done)
    );

    always #5 clk = ~clk;   // 100 MHz

    // Drive one sample
    task send(input signed [DATA_WIDTH-1:0] value);
        begin
            @(posedge clk);
            sample_in    <= value;
            sample_valid <= 1'b1;
            @(posedge clk);
            sample_valid <= 1'b0;
        end
    endtask

    initial begin
        $dumpfile("waves/fault.vcd");
        $dumpvars(0, tb_fault_detect);

        // Reset
        repeat (3) @(posedge clk);
        rst_n = 1;

        //  Window 1: healthy, low amplitude 
        $display("[%0t] Window 1: healthy signal", $time);
        for (i = 0; i < WINDOW_SIZE; i = i + 1)
            send((i % 2) ? 12'sd150 : -12'sd150);

        @(posedge clk);
        if (fault_flag)
            $display("FAIL: flag asserted on healthy data");
        else
            $display("PASS: no fault on healthy data (exceed_count seen = %0d)", exceed_count);

        //  Window 2: faulty, high amplitude 
        $display("[%0t] Window 2: faulty signal", $time);
        for (i = 0; i < WINDOW_SIZE; i = i + 1)
            send((i % 2) ? 12'sd900 : -12'sd900);

        @(posedge clk);
        if (fault_flag)
            $display("PASS: fault detected on faulty data");
        else
            $display("FAIL: flag not asserted on faulty data");

        repeat (10) @(posedge clk);
        $finish;
    end

endmodule
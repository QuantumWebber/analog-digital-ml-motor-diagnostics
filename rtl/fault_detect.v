

module fault_detect #(
    parameter DATA_WIDTH  = 12,     
    parameter THRESHOLD   = 12'd400, 
    parameter WINDOW_SIZE = 1024,    
    parameter FAULT_LIMIT = 100      
)(
    input  wire                          clk,
    input  wire                          rst_n,
    input  wire                          sample_valid,
    input  wire signed [DATA_WIDTH-1:0]  sample_in,

    output reg                           fault_flag,
    output reg  [15:0]                   exceed_count,
    output reg                           window_done
);

    reg [15:0] sample_count;
    wire [DATA_WIDTH-1:0] abs_sample;
    wire exceeded;

    // Absolute value of the signed input sample
    assign abs_sample = sample_in[DATA_WIDTH-1] ? (~sample_in + 1'b1)
                                                : sample_in;

    // Comparator
    assign exceeded = (abs_sample > THRESHOLD);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sample_count <= 16'd0;
            exceed_count <= 16'd0;
            fault_flag   <= 1'b0;
            window_done  <= 1'b0;
        end
        else if (sample_valid) begin
            window_done <= 1'b0;

            if (sample_count == WINDOW_SIZE - 1) begin
                // End of window: evaluate and restart
                window_done <= 1'b1;
                if ((exceed_count + (exceeded ? 16'd1 : 16'd0)) > FAULT_LIMIT)
                    fault_flag <= 1'b1;   // latched until reset

                sample_count <= 16'd0;
                exceed_count <= 16'd0;
            end
            else begin
                sample_count <= sample_count + 1'b1;
                if (exceeded)
                    exceed_count <= exceed_count + 1'b1;
            end
        end
        else begin
            window_done <= 1'b0;
        end
    end

endmodule